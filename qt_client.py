import os
from time import sleep
import threading
from elkpy import sushicontroller as sc
from elkpy import sushi_info_types as sushi
import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from functools import partial
from enum import IntEnum

SUSHI_ADDRESS = ('localhost:51051')
# Get protofile to generate grpc library
proto_file = os.environ.get('SUSHI_GRPC_ELKPY_PROTO')
if proto_file is None:
    print('Environment variable SUSHI_GRPC_ELKPY_PROTO not defined, set it to point the .proto definition')
    sys.exit(-1)

SYNCMODES = ['Internal', 'Midi', 'Gate', 'Link']
PLUGIN_TYPES = ['Internal', 'Vst2x', 'Vst3x', 'LV2']

# Number of columns of parameters to display per processor
# 1-3 works reasonably well
MAX_COLUMNS              = 1

PROCESSOR_WIDTH          = 300
PARAMETER_VALUE_WIDTH    = 80
ICON_BUTTON_WIDTH        = 30
SLIDER_HEIGHT            = 15
SLIDER_MIN_WIDTH         = 100
PAN_SLIDER_WIDTH         = 60

# Slider values are ints in QT, so we need to scale with an integer factor to get 0-1 floats
SLIDER_MAX_VALUE         = 1024

class Direction(IntEnum):
    UP = 1
    DOWN = 2


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller
        self.setWindowTitle('Sushi')
        #self.setGeometry(100,100,1000,1000)

        self._window_layout = QVBoxLayout()
        self._central_widget = QWidget(self)
        self._central_widget.setLayout(self._window_layout)
        self.setCentralWidget(self._central_widget)

        self.tpbar = TransportBarWidget(self._controller)
        self._window_layout.addWidget(self.tpbar)
        self.tracks = {}
        self._track_layout = QHBoxLayout(self)
        self._window_layout.addLayout(self._track_layout)

        self._create_tracks()

    def delete_track(self, track_id):
        track = self.tracks.pop(track_id)
        track.deleteLater() # Otherwise traces are left hanging
        self._track_layout.removeWidget(track)

    def create_track(self, track_info):
        if (track_info.id not in self.tracks):
            track = TrackWidget(self._controller, track_info, self)
            self._track_layout.addWidget(track)
            self.tracks[track_info.id] = track

    def create_processor_on_track(self, plugin_info, track_id):
        self.tracks[track_id].create_processor(plugin_info)

    def _create_tracks(self):
        tracks = self._controller.get_tracks()
        for t in tracks:
            self.create_track(t)
        

class TransportBarWidget(QGroupBox):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)
        self._create_widgets()

    def _create_widgets(self):
        self._syncmode_label = QLabel('Sync mode', self)
        self._layout.addWidget(self._syncmode_label)
        self._syncmode = QComboBox(self)
        for mode in SYNCMODES:
            self._syncmode.addItem(mode)

        self._layout.addWidget(self._syncmode)
        self._tempo_label = QLabel('Tempo', self)
        self._layout.addWidget(self._tempo_label)

        self._tempo = QDoubleSpinBox(self)
        self._tempo.setRange(20, 999)
        self._tempo.setValue(self._controller.get_tempo())
        self._layout.addWidget(self._tempo)

        self._stop_button = QPushButton('', self)
        self._stop_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaStop')))
        self._stop_button.setCheckable(True)
        self._layout.addWidget(self._stop_button)

        self._play_button = QPushButton('', self)
        self._play_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
        self._play_button.setCheckable(True)
        self._layout.addWidget(self._play_button)

        self._add_track_button = QPushButton('New Track', self)
        self._layout.addWidget(self._add_track_button)


        self._layout.addStretch(0)
        self._connect_signals()

    def _connect_signals(self):
        self._play_button.clicked.connect(self._controller.set_playing)
        self._stop_button.clicked.connect(self._controller.set_stopped)
        self._syncmode.currentTextChanged.connect(self._controller.set_sync_mode_txt)
        self._tempo.valueChanged.connect(self._controller.set_tempo)
        self._add_track_button.clicked.connect(self._controller.add_track)

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
        self.processors = {}
        self._create_processors(track_info)
        self._create_common_controls(track_info)
        self._connect_signals()

    def create_processor(self, proc_info):
        if proc_info.id not in self.processors:
            processor = ProcessorWidget(self._controller, proc_info, self._id, self)
            self._proc_layout.insertWidget(self._proc_layout.count() - 1, processor)
            self.processors[proc_info.id] = processor

    def _create_processors(self, track_info):
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        scroll.setFrameShape(QFrame.NoFrame)

        self._proc_layout = QVBoxLayout(self)
        frame = QWidget(self)
        frame.setLayout(self._proc_layout)
        frame.setContentsMargins(0,0,0,0)
        frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        scroll.setWidget(frame)
        self._layout.addWidget(scroll)

        processors = self._controller.get_track_processors(track_info.id)
        for p in processors:
            processor = ProcessorWidget(self._controller, p, track_info.id, self)
            self._proc_layout.addWidget(processor, 0)
            self.processors[p.id] = processor

        self._proc_layout.addStretch()

    def _create_common_controls(self, track_info):
        pan_gain_layout = QHBoxLayout(self)
        pan_gain_layout.setContentsMargins(0,0,0,0)
        pan_gain_box = QGroupBox('Master', self)
        pan_gain_box.setMaximumHeight(220)
        pan_gain_box.setLayout(pan_gain_layout)
        self._layout.addWidget(pan_gain_box)
        self._pan_gain = [PanGainWidget(self._id, 'Main Bus', 0, 1, self._controller, self)]
        pan_gain_layout.addWidget(self._pan_gain[0], 0, Qt.AlignLeft)

        # Create 1 pan/gain control per extra output bus
        for bus in range(1, track_info.output_busses):
            gain_id = self._controller.get_parameter_id(track_info.id, 'gain_sub_' + str(bus))
            pan_id = self._controller.get_parameter_id(track_info.id, 'pan_sub_' + str(bus))
            pan_gain = PanGainWidget(self._id, 'Sub Bus ' + str(bus), gain_id, pan_id, self._controller, self)
            pan_gain_layout.addWidget(pan_gain)
            self._pan_gain.append(pan_gain)

        self._track_buttons = QHBoxLayout(self)
        self._layout.addLayout(self._track_buttons)
        #self._mute_button = QPushButton('Mute', self)
        #self._track_buttons.addWidget(self._mute_button)
        #self._mute_button.setCheckable(True)
        #self._mute_button.setChecked(self._controller.get_processor_bypass_state(self._id))
        self._delete_button = QPushButton('Delete', self)
        self._track_buttons.addWidget(self._delete_button)
        self._add_plugin_button = QPushButton('Add Plugin', self)
        self._track_buttons.addWidget(self._add_plugin_button)
        self._track_buttons.addStretch(0)

    def _connect_signals(self):
        #self._mute_button.clicked.connect(self.mute_track)
        self._delete_button.clicked.connect(self.delete_track)
        self._add_plugin_button.clicked.connect(self.add_plugin)

    def mute_track(self, arg):
        #state = self._mute_button.isChecked()
        self._controller.set_processor_bypass_state(self._id, state)

    def delete_track(self, arg):
        self._controller.delete_track(self._id)

    def add_plugin(self, arg):
        self._controller.add_plugin(self._id)

    def delete_processor(self, processor_id):
        p = self.processors.pop(processor_id)
        p.deleteLater() # Otherwise traces are left hanging
        self._proc_layout.removeWidget(p)

    def move_processor(self, processor_id, direction):
        p = self.processors[processor_id]
        index = self._proc_layout.indexOf(p)
        
        if direction == Direction.UP and index > 0:
            self._proc_layout.removeWidget(p)
            self._proc_layout.insertWidget(index - 1, p)

        # There is a 'hidden' strech element that should always remain at the end
        # for layout purposes, so never move the processor past that element.
        elif direction == Direction.DOWN and index < self._proc_layout.count() - 2:
            self._proc_layout.removeWidget(p)
            self._proc_layout.insertWidget(index + 1, p)


class ProcessorWidget(QGroupBox):
    def __init__(self, controller, processor_info, track_id, parent):
        super().__init__(processor_info.name, parent)
        self.setFixedWidth(PROCESSOR_WIDTH * MAX_COLUMNS)
        # Make sure the ProcessorWidget doesn't expand to much, as that looks ugly
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self._controller = controller
        self._id = processor_info.id
        self._track_id = track_id
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

        self._mute_button = QPushButton(self)
        self._mute_button.setCheckable(True)
        self._mute_button.setChecked(self._controller.get_processor_bypass_state(self._id))
        self._mute_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaVolumeMuted')))
        self._mute_button.setFixedWidth(ICON_BUTTON_WIDTH)
        self._mute_button.setToolTip('Mute processor')
        common_layout.addWidget(self._mute_button)

        self._delete_button = QPushButton(self)
        self._delete_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCloseButton')))
        self._delete_button.setFixedWidth(ICON_BUTTON_WIDTH)
        self._delete_button.setToolTip('Delete processor')
        common_layout.addWidget(self._delete_button)

        self._up_button = QPushButton('', self)
        self._up_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowUp')))
        self._up_button.setToolTip('Move processor up')
        self._up_button.setFixedWidth(ICON_BUTTON_WIDTH)
        common_layout.addWidget(self._up_button)

        self._down_button = QPushButton('', self)
        self._down_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowDown')))
        self._down_button.setToolTip('Move processor down')
        self._down_button.setFixedWidth(ICON_BUTTON_WIDTH)
        common_layout.addWidget(self._down_button)
    

        self._program_selector = QComboBox(self)
        common_layout.addWidget(self._program_selector)
        if processor_info.program_count > 0:
            for program in self._controller.get_processor_programs(self._id):
                self._program_selector.addItem(program.name)
            
        else:
            self._program_selector.addItem('No programs')
    
    def _connect_signals(self):
        self._mute_button.clicked.connect(self.mute_processor_clicked)
        self._program_selector.currentIndexChanged.connect(self.program_selector_changed)
        self._delete_button.clicked.connect(self.delete_processor_clicked)
        self._up_button.clicked.connect(self.up_clicked)
        self._down_button.clicked.connect(self.down_clicked)

    def delete_processor_clicked(self):
        self._controller.delete_processor(self._track_id, self._id)

    def up_clicked(self):
        self._controller.move_processor(self._track_id, self._id, Direction.UP)

    def down_clicked(self):
        self._controller.move_processor(self._track_id, self._id, Direction.DOWN)

    def mute_processor_clicked(self, arg):
        state = self._mute_button.isChecked()
        self._controller.set_processor_bypass_state(self._id, state)        

    def program_selector_changed(self, program_id):
        self._controller.set_processor_program(self._id, program_id)
        for param in self._parameters:
            param.refresh()


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

        self._value_label = QLabel('0.0' + parameter_info.unit, self)
        self._value_label.setFixedWidth(PARAMETER_VALUE_WIDTH)
        self._value_label.setAlignment(Qt.AlignRight)
        self._layout.addWidget(self._value_label)
        self._layout.setContentsMargins(0,0,0,0)

        value = self._controller.get_parameter_value(self._processor_id, self._id)
        self._value_slider.setValue(value * SLIDER_MAX_VALUE)
        self.refresh()
        self._connect_signals()

    def _connect_signals(self):
        self._value_slider.valueChanged.connect(self.value_changed)

    def refresh(self):
        value = self._controller.get_parameter_value(self._processor_id, self._id)
        self._value_slider.setValue(value * SLIDER_MAX_VALUE)
        txt_value = self._controller.get_parameter_value_as_string(self._processor_id, self._id)
        self._value_label.setText(txt_value + ' ' + self._unit)

    def value_changed(self):
        value = float(self._value_slider.value()) / SLIDER_MAX_VALUE
        self._controller.set_parameter_value(self._processor_id, self._id, value)
        txt_value = self._controller.get_parameter_value_as_string(self._processor_id, self._id)
        self._value_label.setText(txt_value + ' ' + self._unit)


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

        self._gain_label = QLabel('', self)
        self._layout.addWidget(self._gain_label, 0, Qt.AlignHCenter)

        self._pan_slider = QSlider(Qt.Orientation.Horizontal, self)
        self._pan_slider.setFixedWidth(PAN_SLIDER_WIDTH)
        self._pan_slider.setRange(0, SLIDER_MAX_VALUE)
        self._pan_slider.setValue(SLIDER_MAX_VALUE / 2)
        self._layout.addWidget(self._pan_slider, 0, Qt.AlignHCenter)

        self._pan_label = QLabel('', self)
        self._layout.addWidget(self._pan_label, 0, Qt.AlignHCenter)

        value = self._controller.get_parameter_value(self._processor_id, self._pan_id)
        self._pan_slider.setValue(value * SLIDER_MAX_VALUE)
        self.pan_changed()
        value = self._controller.get_parameter_value(self._processor_id, self._gain_id)
        self._gain_slider.setValue(value * SLIDER_MAX_VALUE)
        self.gain_changed()
        self._connect_signals()

    def _connect_signals(self):
        self._pan_slider.valueChanged.connect(self.pan_changed)
        self._gain_slider.valueChanged.connect(self.gain_changed)

    def _update_values(self):
        value = self._controller.get_parameter_value(self._processor_id, self._pan_id)
        self._pan_slider.setValue(value * SLIDER_MAX_VALUE)
        self.pan_changed()
        value = self._controller.get_parameter_value(self._processor_id, self._gain_id)
        self._gain_slider.setValue(value * SLIDER_MAX_VALUE)
        self.gain_changed()

    def pan_changed(self):
        value = float(self._pan_slider.value()) / SLIDER_MAX_VALUE
        self._controller.set_parameter_value(self._processor_id, self._pan_id, value)
        pan_value = self._controller.get_parameter_value(self._processor_id, self._pan_id)
        self._pan_label.setText(str(pan_value))

    def gain_changed(self):
        value = float(self._gain_slider.value()) / SLIDER_MAX_VALUE
        self._controller.set_parameter_value(self._processor_id, self._gain_id, value)
        txt_gain = self._controller.get_parameter_value_as_string(self._processor_id, self._gain_id)
        self._gain_label.setText(txt_gain + ' ' + 'dB')


class AddTrackDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Add new stereo track')

        self._ok = False
        self._name = ''
        self._has_input = True
        self._input_bus = 0
        self._output_bus = 0

        self._layout = QGridLayout(self)
        self.setLayout(self._layout)

        name_label = QLabel('Name', self)
        self._layout.addWidget(name_label, 0,0)
        self._name_entry = QLineEdit(self)
        self._layout.addWidget(self._name_entry,0,1)

        has_input_label = QLabel('Has Input')
        self._layout.addWidget(has_input_label, 2, 0)
        self._has_input_check = QCheckBox('', self)
        self._has_input_check.setChecked(True)
        self._layout.addWidget(self._has_input_check, 2, 1)

        input_label = QLabel('Input bus', self)
        self._layout.addWidget(input_label, 1,0)
        self._input_spin_box = QSpinBox(self)
        self._layout.addWidget(self._input_spin_box,1,1)

        output_label = QLabel('Output bus', self)
        self._layout.addWidget(output_label, 3,0)
        self._output_spin_box = QSpinBox(self)
        self._layout.addWidget(self._output_spin_box,3,1)

        self._ok_button = QPushButton('Ok', self)
        self._layout.addWidget(self._ok_button,4,1)
        self._cancel_button = QPushButton('Cancel', self)
        self._layout.addWidget(self._cancel_button,4,0)
        
        self._connect_signals()

    def _connect_signals(self):
        self._name_entry.textChanged.connect(self.name_changed)
        self._has_input_check.stateChanged.connect(self.checkbox_toggled)
        self._input_spin_box.valueChanged.connect(self.input_changed)
        self._output_spin_box.valueChanged.connect(self.output_changed)
        self._ok_button.clicked.connect(self.ok_clicked)
        self._cancel_button.clicked.connect(self.cancel_clicked)

    def checkbox_toggled(self, state):
        self._has_input = state
        if self._has_input:
            self._input_spin_box.setEnabled(True)
        else:
            self._input_spin_box.setEnabled(False)

    def name_changed(self, name):
        self._name = name

    def input_changed(self, value):
        self._input_bus = value

    def output_changed(self, value):
        self._output_bus = value

    def ok_clicked(self):
        self._ok = True
        self.close()

    def cancel_clicked(self):
        self.close()

    def get_data(self):
        return self._ok, self._name, self._has_input, self._input_bus, self._output_bus


class AddPluginDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Add new plugin')

        self._ok = False
        self._type = sushi.PluginType.INTERNAL
        self._uid = ''
        self._path = ''
        self._name = ''

        self._layout = QGridLayout(self)
        self.setLayout(self._layout)

        type_label = QLabel('Type', self)
        self._layout.addWidget(type_label, 0, 0)
        self._type_box = QComboBox(self)
        self._layout.addWidget(self._type_box, 0, 1)
        for t in PLUGIN_TYPES:
            self._type_box.addItem(t)

        name_label = QLabel('Name', self)
        self._layout.addWidget(name_label, 1,0)
        self._name_entry = QLineEdit(self)
        self._name_entry.setMinimumWidth(200)
        self._layout.addWidget(self._name_entry,1,1)

        self._uid_label = QLabel('Uid', self)
        self._layout.addWidget(self._uid_label, 2,0)
        self._uid_entry = QLineEdit(self)
        self._layout.addWidget(self._uid_entry,2,1)

        self._path_label = QLabel('Path', self)
        self._layout.addWidget(self._path_label, 3,0)
        self._path_entry = QLineEdit(self)
        self._path_entry.setEnabled(False)
        self._layout.addWidget(self._path_entry,3,1)

        self._ok_button = QPushButton('Ok', self)
        self._layout.addWidget(self._ok_button,4,1)
        self._cancel_button = QPushButton('Cancel', self)
        self._layout.addWidget(self._cancel_button,4,0)
        
        self._connect_signals()

    def _connect_signals(self):
        self._type_box.currentIndexChanged.connect(self.type_changed)
        self._name_entry.textChanged.connect(self.name_changed)
        self._path_entry.textChanged.connect(self.path_changed)
        self._uid_entry.textChanged.connect(self.uid_changed)
        self._ok_button.clicked.connect(self.ok_clicked)
        self._cancel_button.clicked.connect(self.cancel_clicked)

    def type_changed(self, type_index):
        type = type_index + 1
        self._type = type
        if (type == sushi.PluginType.INTERNAL):
            self._path_entry.setEnabled(False)
            self._uid_entry.setEnabled(True)

        elif (type == sushi.PluginType.VST2X):
            self._path_entry.setEnabled(True)
            self._uid_entry.setEnabled(False)

        elif (type == sushi.PluginType.VST3X):
            self._path_entry.setEnabled(True)
            self._uid_entry.setEnabled(True)

        elif (type == sushi.PluginType.LV2):
            self._path_entry.setEnabled(False)
            self._uid_entry.setEnabled(True)


    def name_changed(self, value):
        self._name = value

    def uid_changed(self, value):
        self._uid = value

    def path_changed(self, value):
        self._path = value

    def ok_clicked(self):
        self._ok = True
        self.close()

    def cancel_clicked(self):
        self.close()

    def get_data(self):
        return self._ok, self._type, self._name, self._path, self._uid


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

    def delete_processor(self, track_id, processor_id):
        self.delete_processor_from_track(processor_id, track_id)
        self._view.tracks[track_id].delete_processor(processor_id)

    def delete_track(self, track_id):
        super().delete_track(track_id)
        self._view.delete_track(track_id)

    def add_track(self, arg):
        dialog = AddTrackDialog(self._view)
        dialog.exec_()
        ok, name, has_input, input_bus, output_bus = dialog.get_data()
        if ok:
            try:
                self.create_stereo_track(name, output_bus, has_input, input_bus)
                #When notifications are working, we can wait for a notification instead
                sleep(0.2)
                new_track = self.get_tracks()[-1]
                self._view.create_track(new_track)

            except e:
                print('Error creating track: {}'.format(e))

    def add_plugin(self, track_id):
        dialog = AddPluginDialog(self._view)
        dialog.exec_()
        ok, type, name, path, uid = dialog.get_data()
        print(dialog.get_data())
        if ok:
            try:
                self.create_processor_on_track(name, uid, path, type, track_id, True, 0)
                #When notifications are working, we can wait for a notification instead
                sleep(0.4)
                new_plugin = self.get_track_processors(track_id)[-1]
                self._view.create_processor_on_track(new_plugin, track_id)

            except e:
                print('Error creating plugin: {}'.format(e))   


    def move_processor(self, track_id, processor_id, direction):
        track_info = self.get_track_info(track_id)
        index = track_info.processors.index(processor_id)

        proc_count = len(track_info.processors)
        if (direction == Direction.UP and index == 0) or (direction == direction.DOWN and index == proc_count - 1):
            # Processor is not in a place where it can be moved
            return

        # only true if moving down and processor position is second to last
        add_to_back = direction == Direction.DOWN and index == proc_count - 2
        before_processor = 0 
        if direction == Direction.UP:
            before_processor = track_info.processors[index - 1] 
        elif not add_to_back:
            before_processor = track_info.processors[index + 2]

        self.move_processor_on_track(processor_id, track_id, track_id, add_to_back, before_processor)
        track_info = self.get_track_info(track_id)

        self._view.tracks[track_id].move_processor(processor_id, direction)

    def set_sync_mode_txt(self, txt_mode):
        if txt_mode == 'Internal':
            self.set_sync_mode(sushi.SyncMode.INTERNAL)
        elif txt_mode == 'Link':
            self.set_sync_mode(sushi.SyncMode.LINK)
        if txt_mode == 'Midi':
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