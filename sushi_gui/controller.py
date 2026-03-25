import time
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QFileDialog
from elkpy.sushicontroller import SushiController
from elkpy import sushi_info_types as sushi
from .dialogs import AddTrackDialog, AddPluginDialog, AddCustomPluginDialog
from .constants import Direction

if TYPE_CHECKING:
    from sushi_gui.main_window import MainWindow


# Expand the controller with a few convenience functions that better match our use case
class Controller(SushiController):
    """This expands on the SushiController class that comes with elkpy by adding to it QT specific
    functionality, like signal handling"""

    def __init__(self, address: str, proto_file: str | None = None) -> None:
        if proto_file:
            super().__init__(address, proto_file)
        else:
            super().__init__(address)
        self._view: MainWindow

    def emit_track_notification(self, notification) -> None:
        try:
            self._view.track_notification_received.emit(notification)
        # Note, if an exception in a notification handler is not caught, that notification stops working
        except Exception as e:
            print(e)

    def emit_processor_notification(self, notification) -> None:
        try:
            self._view.processor_notification_received.emit(notification)
        except Exception as e:
            print(e)

    def emit_parameter_notification(self, notification) -> None:
        try:
            self._view.parameter_notification_received.emit(notification)
        except Exception as e:
            print(e)

    def emit_transport_notification(self, notification) -> None:
        try:
            self._view.transport_notification_received.emit(notification)
        except Exception as e:
            print(e)

    def emit_timing_notification(self, notification) -> None:
        try:
            self._view.timing_notification_received.emit(notification)
        except Exception as e:
            print(e)

    def emit_property_notification(self, notification) -> None:
        try:
            self._view.property_notification_received.emit(notification)
        except Exception as e:
            print(e)

    def subscribe_to_notifications(self) -> None:
        self.notifications.subscribe_to_track_changes(self.emit_track_notification)
        self.notifications.subscribe_to_processor_changes(
            self.emit_processor_notification
        )
        self.notifications.subscribe_to_parameter_updates(
            self.emit_parameter_notification
        )
        self.notifications.subscribe_to_transport_changes(
            self.emit_transport_notification
        )
        self.notifications.subscribe_to_timing_updates(self.emit_timing_notification)
        self.notifications.subscribe_to_property_updates(
            self.emit_property_notification
        )
        self.timings.set_timings_enabled(True)
        self.timings.reset_all_timings()

    def set_playing(self) -> None:
        self.transport.set_playing_mode(2)

    def set_stopped(self) -> None:
        self.transport.set_playing_mode(1)

    def delete_processor(self, track_id: int, processor_id: int) -> None:
        self.audio_graph.delete_processor_from_track(processor_id, track_id)

    def delete_track(self, track_id: int) -> None:
        self.audio_graph.delete_track(track_id)

    def add_track(self) -> None:
        dialog = AddTrackDialog(self._view)
        if dialog.exec_():
            track_type = dialog.track_type.currentText()
            inputs = dialog.inputs_sb.value()
            outputs = dialog.outputs_sb.value()
            name = dialog.name_entry.text().strip()

            if track_type == "Multibus":
                self.audio_graph.create_multibus_track(name, outputs, inputs)
            elif track_type == "Stereo":
                self.audio_graph.create_track(name, 2)
            elif track_type == "Mono":
                self.audio_graph.create_track(name, 1)

            while True:
                try:
                    track_id = self.audio_graph.get_track_id(name)
                    break
                except Exception as e:
                    print(e)
                    time.sleep(0.3)

            self.audio_routing.connect_output_channel_from_track(track_id, 0, 0)
            if track_type == "Stereo":
                self.audio_routing.connect_output_channel_from_track(track_id, 1, 1)
            print(f"Connected audio outputs on track {name}")

    def add_plugin(self, track_id: int) -> None:
        dialog = AddPluginDialog(self._view)
        if dialog.exec_():
            plug = dialog.selected_plugin
            name = dialog.plugin_name

            # Get uid and path, defaulting to None if not present
            uid = plug.get("uid", None)
            path = plug.get("path", None)

            # Set plugin type based on the "type" field
            plugin_type_str = plug.get("type", "internal").lower()
            if plugin_type_str == "vst2x":
                p_type = sushi.PluginType.VST2X
            elif plugin_type_str == "vst3x":
                p_type = sushi.PluginType.VST3X
            elif plugin_type_str == "lv2":
                p_type = sushi.PluginType.LV2
            else:  # "internal" or default
                p_type = sushi.PluginType.INTERNAL

            # Ensure exactly one of uid or path is not None
            if p_type == sushi.PluginType.VST3X:
                if uid is None or path is None:
                    print(f"Error: VST3X plugin must have both 'uid' and 'path', got uid={uid}, path={path}")
                    return
            else:
                if (uid is None and path is None) or (uid is not None and path is not None):
                    print(f"Error: Plugin must have exactly one of 'uid' or 'path', got uid={uid}, path={path}")
                    return

            try:
                self.audio_graph.create_processor_on_track(
                    name, uid, path, p_type, track_id, 0, True
                )
            except Exception as e:
                print("Error creating plugin: {}".format(e))

    def add_custom_plugin(self, track_id: int) -> None:
        dialog = AddCustomPluginDialog(self._view)
        if dialog.exec_():
            name = dialog.name_entry.text().strip()
            uid = dialog.uid_entry.text().strip()
            path = dialog.path_entry.text().strip()
            p_type = dialog.plugin_type
            try:
                self.audio_graph.create_processor_on_track(
                    name, uid, path, p_type, track_id, 0, True
                )
            except Exception as e:
                print("Error creating plugin: {}".format(e))

    def move_processor(
        self, track_id: int, processor_id: int, direction: Direction
    ) -> None:
        track_info = self.audio_graph.get_track_info(track_id)
        index = track_info.processors.index(processor_id)

        proc_count = len(track_info.processors)
        if (direction == Direction.UP and index == 0) or (
            direction == direction.DOWN and index == proc_count - 1
        ):
            # Processor is not in a place where it can be moved
            return

        # only true if moving down and processor position is second to last
        add_to_back = direction == Direction.DOWN and index == proc_count - 2
        before_processor = 0
        if direction == Direction.UP:
            before_processor = track_info.processors[index - 1]
        elif not add_to_back:
            before_processor = track_info.processors[index + 2]

        self._view.tracks[track_id].move_processor(processor_id, direction)
        self.audio_graph.move_processor_on_track(
            processor_id, track_id, track_id, before_processor, add_to_back
        )

    def set_sync_mode_txt(self, txt_mode: sushi.SyncMode) -> None:
        if txt_mode == "Internal":
            self.transport.set_sync_mode(sushi.SyncMode.INTERNAL)
        elif txt_mode == "Link":
            self.transport.set_sync_mode(sushi.SyncMode.LINK)
        if txt_mode == "Midi":
            self.transport.set_sync_mode(sushi.SyncMode.MIDI)

    def save_session(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self._view, "Save Session As", "", "")

        if filename:
            if not filename.endswith(".sushi"):
                filename += ".sushi"

            saved_session = self.session.save_binary_session()
            with open(filename, "wb") as f:
                f.write(saved_session)

    def restore_session(self):
        filename, _ = QFileDialog.getOpenFileName(
            self._view, "Load Session", "", "Sushi Files (*.sushi)"
        )

        if filename:
            with open(filename, "rb") as f:
                saved_session = f.read()

            self.session.restore_binary_session(saved_session)

    def set_view(self, view: "MainWindow") -> None:
        self._view = view
