import os
from time import sleep
import threading
from elkpy import sushicontroller as sc
from elkpy import sushi_info_types as sushi
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from functools import partial

SUSHI_ADDRESS = ('localhost:51051')
# Get protofile to generate grpc library
proto_file = os.environ.get('SUSHI_GRPC_ELKPY_PROTO')
if proto_file is None:
    print("Environment variable SUSHI_GRPC_ELKPY_PROTO not defined, set it to point the .proto definition")
    sys.exit(-1)

SYNCMODES = ["Internal", "Midi", "Gate", "Link"]


MAX_COLUMNS              = 1
PARAMETER_VALUE_WIDTH    = 80
SLIDER_HEIGHT            = 15
SLIDER_MIN_WIDTH         = 100
PAN_SLIDER_WIDTH         = 60
# Slider values are ints in QT
SLIDER_MAX_VALUE         = 1024


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller
        self.setWindowTitle('Sushi')
        #self.setGeometry(100,100,1000,1000)

        self._window_layout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self._centralWidget.setLayout(self._window_layout)
        self.setCentralWidget(self._centralWidget)

        self.tpbar = TransportBarWidget(self._controller)
        self._window_layout.addWidget(self.tpbar)
        self._tracks = []
        self._create_tracks()


    def _create_tracks(self):
        self._track_layout = QHBoxLayout(self)
        self._window_layout.addLayout(self._track_layout)
        tracks = self._controller.get_tracks()
        for t in tracks:
            track = TrackWidget(self._controller, t, self)
            self._track_layout.addWidget(track)
            self._tracks.append(track)
        

class TransportBarWidget(QGroupBox):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)
        self._create_widgets()

    def _create_widgets(self):
        self._syncmode_label = QLabel("Sync mode", self)
        self._layout.addWidget(self._syncmode_label)
        self._syncmode = QComboBox(self)
        for mode in SYNCMODES:
            self._syncmode.addItem(mode)

        self._layout.addWidget(self._syncmode)
        self._tempo_label = QLabel("Tempo", self)
        self._layout.addWidget(self._tempo_label)

        self._tempo = QDoubleSpinBox(self)
        self._tempo.setRange(20, 999)
        self._tempo.setValue(self._controller.get_tempo())
        self._layout.addWidget(self._tempo)

        self._stop_button = QPushButton("", self)
        self._stop_button.setIcon(self.style().standardIcon(getattr(QStyle, "SP_MediaStop")))
        self._stop_button.setCheckable(True)
        self._layout.addWidget(self._stop_button)

        self._play_button = QPushButton("", self)
        self._play_button.setIcon(self.style().standardIcon(getattr(QStyle, "SP_MediaPlay")))
        self._play_button.setCheckable(True)
        self._layout.addWidget(self._play_button)

        self._layout.addStretch(0)
        self._connect_signals()

    def _connect_signals(self):
        self._play_button.clicked.connect(self._controller.set_playing)
        self._stop_button.clicked.connect(self._controller.set_stopped)
        self._syncmode.currentTextChanged.connect(self._controller.set_sync_mode_txt)
        self._tempo.valueChanged.connect(self._controller.set_tempo)

    def set_playing(self, playing):
        self._play_button.setChecked(playing)
        self._stop_button.setChecked(not playing)

class TrackWidget(QGroupBox):
    def __init__(self, controller, track_info, parent):
        super().__init__(track_info.name, parent)
        self._id = track_info.id
        self._controller = controller
        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)
        self._processors = []
        self._create_processors(track_info)
        self._create_common_controls(track_info)
        self._connect_signals()

    def _create_processors(self, track_info):
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        #scroll.setMinimumHeight(400)
        scroll.setFrameShape(QFrame.NoFrame)

        proc_layout = QVBoxLayout(self)
        frame = QWidget(self)
        frame.setLayout(proc_layout)
        frame.setContentsMargins(0,0,0,0)
        frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        scroll.setWidget(frame)
        self._layout.addWidget(scroll)

        processors = self._controller.get_track_processors(track_info.id)
        for p in processors:
            processor = ProcessorWidget(self._controller, p, self)
            proc_layout.addWidget(processor)
            self._processors.append(processor)

        #self._layout.addStretch(0)

    def _create_common_controls(self, track_info):
        pan_gain_layout = QHBoxLayout(self)
        pan_gain_layout.setContentsMargins(0,0,0,0)
        pan_gain_box = QGroupBox("Master", self)
        pan_gain_box.setMaximumHeight(220)
        pan_gain_box.setLayout(pan_gain_layout)
        self._layout.addWidget(pan_gain_box)
        self._pan_gain = [PanGainWidget(self._id, "Main Bus", 0, 1, self._controller, self)]
        pan_gain_layout.addWidget(self._pan_gain[0], 0, Qt.AlignLeft)

        # Create 1 pan/gain control per extra output bus
        for bus in range(1, track_info.output_busses):
            gain_id = self._controller.get_parameter_id(track_info.id, "gain_sub_" + str(bus))
            pan_id = self._controller.get_parameter_id(track_info.id, "pan_sub_" + str(bus))
            pan_gain = PanGainWidget(self._id, "Sub Bus " + str(bus), gain_id, pan_id, self._controller, self)
            pan_gain_layout.addWidget(pan_gain)
            self._pan_gain.append(pan_gain)

        self._track_buttons = QHBoxLayout(self)
        self._layout.addLayout(self._track_buttons)
        self._mute_button = QPushButton("Mute", self)
        self._track_buttons.addWidget(self._mute_button)
        self._mute_button.setCheckable(True)
        self._mute_button.setChecked(self._controller.get_processor_bypass_state(self._id))
        self._delete_button = QPushButton("Delete", self)
        self._track_buttons.addWidget(self._delete_button)
        self._track_buttons.addStretch(0)

    def _connect_signals(self):
        self._mute_button.clicked.connect(self.mute_track)

    def mute_track(self, arg):
        state = self._mute_button.isChecked()
        self._controller.set_processor_bypass_state(self._id, state)


class ProcessorWidget(QGroupBox):
    def __init__(self, controller, processor_info, parent):
        super().__init__(processor_info.name)
        self._controller = controller
        self._id = processor_info.id
        self._parameters = []
        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)

        self._create_common_controls(processor_info)
        self._create_parameters()
        self._connect_signals()

    def _create_parameters(self):
        parameters = self._controller.get_processor_parameters(self._id)
        param_count = len(parameters)
        param_layout = QHBoxLayout()
        self._layout.addLayout(param_layout)
        for col in range(0, MAX_COLUMNS):
            col_layout = QVBoxLayout()
            param_layout.addLayout(col_layout)
            for p in parameters[col::MAX_COLUMNS]:
                parameter = ParameterWidget(p, self._id, self._controller, self)
                col_layout.addWidget(parameter)
                self._parameters.append(parameter)

            col_layout.addStretch()
        self._layout.addStretch()

    def _create_common_controls(self, processor_info):
        common_layout = QHBoxLayout(self)
        self._layout.addLayout(common_layout)

        self._mute_button = QPushButton("Mute", self)
        self._mute_button.setCheckable(True)
        self._mute_button.setChecked(self._controller.get_processor_bypass_state(self._id))
        common_layout.addWidget(self._mute_button)
        self._delete_button = QPushButton("Delete", self)
        self._delete_button.setCheckable(True)
        common_layout.addWidget(self._delete_button)

        self._up_button = QPushButton("", self)
        self._up_button.setIcon(self.style().standardIcon(getattr(QStyle, "SP_ArrowUp")))
        common_layout.addWidget(self._up_button)
        self._down_button = QPushButton("", self)
        self._down_button.setIcon(self.style().standardIcon(getattr(QStyle, "SP_ArrowDown")))
        common_layout.addWidget(self._down_button)
        #common_layout.addStretch(0)

        if processor_info.program_count > 0:
            program_layout = QHBoxLayout(self)
            self._layout.addLayout(program_layout)
    
            programs = self._controller.get_processor_programs(self._id)
            label = QLabel("Program", self)
            program_layout.addWidget(label)
            self._program_selector = QComboBox(self)
            program_layout.addWidget(self._program_selector)
            program_layout.addStretch(0)
            for program in programs:
                self._program_selector.addItem(program.name)

            self._program_selector.currentIndexChanged.connect(self.program_change)
        
        ##else:
        #    label = QLabel("Plugin doesn't have any programs", self)
        #    common_layout.addWidget(label)


    def _connect_signals(self):
        self._mute_button.clicked.connect(self.mute_processor)

    def mute_processor(self, arg):
        state = self._mute_button.isChecked()
        self._controller.set_processor_bypass_state(self._id, state)        

    def program_change(self, program_id):
        self._controller.set_processor_program(self._id, program_id)
        for param in self._parameters:
            param.update()


class ParameterWidget(QWidget):
    def __init__(self, parameter_info, processor_id, controller, parent):
        super().__init__(parent)
        self._controller = controller
        self._id = parameter_info.id
        self._processor_id = processor_id
        self._unit = parameter_info.unit
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)

        self._name_label = QLabel(parameter_info.name, self)
        self._name_label.setFixedWidth(PARAMETER_VALUE_WIDTH)
        self._layout.addWidget(self._name_label)

        self._value_slider = QSlider(Qt.Orientation.Horizontal, self)
        self._value_slider.setFixedWidth(SLIDER_MIN_WIDTH)
        self._value_slider.setRange(0, SLIDER_MAX_VALUE)
        self._layout.addWidget(self._value_slider)

        self._value_label = QLabel("0.0" + parameter_info.unit, self)
        self._value_label.setFixedWidth(PARAMETER_VALUE_WIDTH)
        self._value_label.setAlignment(Qt.AlignRight)
        self._layout.addWidget(self._value_label)
        self._layout.setContentsMargins(0,0,0,0)

        value = self._controller.get_parameter_value(self._processor_id, self._id)
        self._value_slider.setValue(value * SLIDER_MAX_VALUE)
        self.update()
        self._connect_signals()

    def _connect_signals(self):
        self._value_slider.valueChanged.connect(self.value_changed)

    def update(self):
        value = self._controller.get_parameter_value(self._processor_id, self._id)
        self._value_slider.setValue(value * SLIDER_MAX_VALUE)
        txt_value = self._controller.get_parameter_value_as_string(self._processor_id, self._id)
        self._value_label.setText(txt_value + " " + self._unit)

    def value_changed(self):
        value = float(self._value_slider.value()) / SLIDER_MAX_VALUE
        self._controller.set_parameter_value(self._processor_id, self._id, value)
        txt_value = self._controller.get_parameter_value_as_string(self._processor_id, self._id)
        self._value_label.setText(txt_value + " " + self._unit)

class PanGainWidget(QWidget):
    def __init__(self, processor_id, name, gain_id, pan_id, controller, parent):
        super().__init__(parent)
        self._processor_id = processor_id
        self._gain_id = gain_id
        self._pan_id = pan_id
        self._controller = controller
        self.setFixedWidth(SLIDER_MIN_WIDTH)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0,0,0,0)

        bus_label = QLabel(name, self)
        self._layout.addWidget(bus_label, 0, Qt.AlignHCenter)

        self._gain_slider = QSlider(Qt.Orientation.Vertical, self)
        self._gain_slider.setFixedHeight(80)
        self._gain_slider.setRange(0, SLIDER_MAX_VALUE)
        self._gain_slider.setValue(SLIDER_MAX_VALUE / 2)
        self._layout.addWidget(self._gain_slider, 0, Qt.AlignHCenter)

        self._gain_label = QLabel("", self)
        self._layout.addWidget(self._gain_label, 0, Qt.AlignHCenter)

        self._pan_slider = QSlider(Qt.Orientation.Horizontal, self)
        self._pan_slider.setFixedWidth(PAN_SLIDER_WIDTH)
        self._pan_slider.setRange(0, SLIDER_MAX_VALUE)
        self._pan_slider.setValue(SLIDER_MAX_VALUE / 2)
        self._layout.addWidget(self._pan_slider, 0, Qt.AlignHCenter)

        self._pan_label = QLabel("", self)
        self._layout.addWidget(self._pan_label, 0, Qt.AlignHCenter)

        self.pan_changed()
        self.gain_changed()
        self._connect_signals()

    def _connect_signals(self):
        self._pan_slider.valueChanged.connect(self.pan_changed)
        self._gain_slider.valueChanged.connect(self.gain_changed)

    def pan_changed(self):
        value = float(self._pan_slider.value()) / SLIDER_MAX_VALUE
        self._controller.set_parameter_value(self._processor_id, self._pan_id, value)
        pan_value = self._controller.get_parameter_value(self._processor_id, self._pan_id)
        self._pan_label.setText(str(pan_value))

    def gain_changed(self):
        value = float(self._gain_slider.value()) / SLIDER_MAX_VALUE
        self._controller.set_parameter_value(self._processor_id, self._gain_id, value)
        txt_gain = self._controller.get_parameter_value_as_string(self._processor_id, self._gain_id)
        self._gain_label.setText(txt_gain + " " + "dB")

# Expand the controller with a few convinience functions that better match our use case
class Controller(sc.SushiController):
    def __init__(self, address, proto_file):
        super().__init__(address, proto_file)
        self._view = None

    def set_playing(self):
        self.set_playing_mode(2)
        if not self._view is  None:
            self._view.tpbar.set_playing(True)

    def set_stopped(self):
        self.set_playing_mode(1)
        if not self._view is  None:
            self._view.tpbar.set_playing(False)

    def set_sync_mode_txt(self, txt_mode):
        if txt_mode == "Internal":
            self.set_sync_mode(sushi.SyncMode.INTERNAL)
        elif txt_mode == "Link":
            self.set_sync_mode(sushi.SyncMode.LINK)
        if txt_mode == "Midi":
            self.set_sync_mode(sushi.SyncMode.MIDI)

    def set_view(self, view):
        self._view = view

# Client code
def main():
    app = QApplication(sys.argv)
    controller = Controller(SUSHI_ADDRESS, proto_file)
    window = MainWindow(controller)
    window.show()
    controller.set_view(window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()