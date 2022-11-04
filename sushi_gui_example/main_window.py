from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QMainWindow, QMessageBox
from elkpy.sushicontroller import SushiController
from elkpy import sushi_info_types as sushi
from constants import MODE_PLAYING
from widgets import TransportBarWidget, TrackWidget


class MainWindow(QMainWindow):
    track_notification_received = Signal()
    processor_notification_received = Signal()
    parameter_notification_received = Signal()
    transport_notification_received = Signal()
    timing_notification_received = Signal()
    property_notification_received = Signal()

    def __init__(self, controller: 'SushiController') -> None:
        super().__init__()
        self._controller = controller
        self.setWindowTitle('Sushi')

        self._window_layout = QVBoxLayout()
        self._central_widget = QWidget(self)
        self._central_widget.setLayout(self._window_layout)
        self.setCentralWidget(self._central_widget)

        # Menu / actions
        self.file_menu = self.menuBar().addMenu("&File")
        self.settings_menu = self.menuBar().addMenu("&Settings")
        self.tools_menu = self.menuBar().addMenu("&Tools")
        self.help_menu = self.menuBar().addMenu("&Info")

        save = QAction('Save', self)
        save.triggered.connect(controller.save_session)
        load = QAction('Load', self)
        load.triggered.connect(controller.restore_session)

        self.file_menu.addAction(save)
        self.file_menu.addAction(load)

        about = QAction('About Sushi', self)
        about.triggered.connect(self.show_about_sushi)
        processors = QAction('Show all processors', self)
        processors.triggered.connect(self.show_all_processors)
        tracks = QAction('Show all tracks', self)
        tracks.triggered.connect(self.show_all_tracks)
        inputs = QAction('Show input connections', self)
        inputs.triggered.connect(self.show_inputs)

        self.help_menu.addAction(about)
        self.help_menu.addAction(processors)
        self.help_menu.addAction(tracks)
        self.help_menu.addAction(inputs)

        self.tpbar = TransportBarWidget(self._controller)
        self._window_layout.addWidget(self.tpbar)
        self.tracks = {}
        self._track_layout = QHBoxLayout(self)
        self._window_layout.addLayout(self._track_layout)

        self.track_notification_received.connect(self.process_track_notification)
        self.processor_notification_received.connect(self.process_processor_notification)
        self.parameter_notification_received.connect(self.process_parameter_notification)
        self.transport_notification_received.connect(self.process_transport_notification)
        self.timing_notification_received.connect(self.process_timing_notification)
        self.property_notification_received.connect(self.process_property_notification)

        self._create_tracks()

    def delete_track(self, track_id: int) -> None:
        track = self.tracks.pop(track_id)
        track.deleteLater() # Otherwise traces are left hanging
        self._track_layout.removeWidget(track)

    def create_track(self, track_info: sushi.TrackInfo) -> None:
        if track_info.id not in self.tracks:
            track = TrackWidget(self._controller, track_info, self)
            self._track_layout.addWidget(track)
            self.tracks[track_info.id] = track

    def create_processor_on_track(self, plugin_info: sushi.ProcessorInfo, track_id: int) -> None:
        self.tracks[track_id].create_processor(plugin_info)

    def _create_tracks(self) -> None:
        tracks = self._controller.audio_graph.get_all_tracks()
        for t in tracks:
            self.create_track(t)

    def show_about_sushi(self) -> None:
        version = self._controller.system.get_sushi_version()
        build_info = self._controller.system.get_build_info()
        audio_inputs = self._controller.system.get_input_audio_channel_count()
        audio_outputs = self._controller.system.get_output_audio_channel_count()

        about = QMessageBox()
        about.setText(f"Sushi version: {version}\n"
                      f"Buidl info: {build_info}\n"
                      f"Audio input count: {audio_inputs}\n"
                      f"Audio output count: {audio_outputs}")
        about.exec_()

    def show_all_processors(self) -> None:
        r = self._controller.audio_graph.get_all_processors()
        info = QMessageBox()
        info.setText(f"{r}")
        info.exec_()

    def show_all_tracks(self) -> None:
        r = self._controller.audio_graph.get_all_tracks()
        info = QMessageBox()
        info.setText(f"{r}")
        info.exec_()

    def show_inputs(self) -> None:
        r = self._controller.audio_routing.get_all_input_connections()
        info = QMessageBox()
        info.setText(f"{r}")
        info.exec_()

    def process_track_notification(self, n) -> None:
        if n.action == 1:   # TRACK_ADDED
            for t in self._controller.audio_graph.get_all_tracks():
                if t.id == n.track.id:
                    self.create_track(t)
                    break
        elif n.action == 2:  # TRACK_DELETED
            self.delete_track(n.track.id)

    def process_processor_notification(self, n) -> None:
        if n.action == 1:  # PROCESSOR_ADDED
            for t in self._controller.audio_graph.get_track_processors(n.parent_track.id):
                if t.id == n.processor.id:
                    self.create_processor_on_track(t, n.parent_track.id)
                    break
        elif n.action == 2:  # PROCESSOR_DELETED
            self.tracks[n.parent_track.id].delete_processor(n.processor.id)

    def process_parameter_notification(self, n) -> None:
        for id, track in self.tracks.items():
            if n.parameter.processor_id == id:
                track.handle_parameter_notification(n)

            elif n.parameter.processor_id in track.processors:
                track.processors[n.parameter.processor_id].handle_parameter_notification(n)

    def process_transport_notification(self, n) -> None:
        if n.HasField('tempo'):
            self.tpbar.set_tempo(n.tempo)

        elif n.HasField('playing_mode'):
            self.tpbar.set_playing(n.playing_mode.mode == MODE_PLAYING)

    def process_timing_notification(self, n) -> None:
        self.tpbar.set_cpu_value(n.average)

    def process_property_notification(self, n) -> None:
        for t, v in self.tracks.items():
            if n.property.processor_id in v.processors:
                v.processors[n.property.processor_id].handle_property_notification(n)
