from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QStyle, QPushButton, \
    QVBoxLayout, QScrollArea, QAbstractScrollArea, QSizePolicy, QSlider, QWidget, QLineEdit, QFileDialog, QFrame

from elkpy.sushicontroller import SushiController
from elkpy import sushi_info_types as sushi

from constants import SYNCMODES, Direction, PROCESSOR_WIDTH, MAX_COLUMNS, ICON_BUTTON_WIDTH, PARAMETER_VALUE_WIDTH, \
    SLIDER_MIN_WIDTH, SLIDER_MAX_VALUE, PAN_SLIDER_WIDTH


class TransportBarWidget(QGroupBox):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self._controller = None
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)
        self._create_widgets()

    def initialize(self):
        self._controller = self._parent._controller
        self._tempo.setValue(self._controller.transport.get_tempo())
        self._connect_signals()

    def _create_widgets(self) -> None:
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

        self._cpu_meter = QLabel("Cpu: -", self)
        self._layout.addWidget(self._cpu_meter)

        self._sushi_ip_lbl = QLabel("Sushi IP:", self)
        self._sushi_ip_tbox = QLineEdit(self)
        self._sushi_ip_tbox.setText(self._parent.current_sushi_ip)
        self._layout.addWidget(self._sushi_ip_lbl)
        self._layout.addWidget(self._sushi_ip_tbox)

        self._layout.addStretch(0)
        self._sushi_ip_tbox.editingFinished.connect(self.set_sushi_ip)

    def _connect_signals(self) -> None:
        self._play_button.clicked.connect(self._controller.set_playing)
        self._stop_button.clicked.connect(self._controller.set_stopped)
        self._syncmode.currentTextChanged.connect(self._controller.set_sync_mode_txt)
        self._tempo.valueChanged.connect(self._controller.transport.set_tempo)
        self._add_track_button.clicked.connect(self._controller.add_track)

    def set_playing(self, playing: bool) -> None:
        self._play_button.setChecked(playing)
        self._stop_button.setChecked(not playing)

    def set_tempo(self, tempo: float) -> None:
        self._tempo.setValue(tempo)

    def set_cpu_value(self, value: float) -> None:
        self._cpu_meter.setText(f"Cpu: {value * 100:.1f}%")

    def set_sushi_ip(self) -> None:
        print(self._sushi_ip_tbox.text())
        if len(self._sushi_ip_tbox.text().split(':')) <= 1:
            self._parent.current_sushi_ip = self._sushi_ip_tbox.text() + ':51051'
        else:
            self._parent.current_sushi_ip = self._sushi_ip_tbox.text()

        self._parent.setup_sushi_controller()


class TrackWidget(QGroupBox):
    def __init__(self, controller: 'SushiController', track_info: sushi.TrackInfo, parent: QWidget) -> None:
        super().__init__(track_info.name, parent)
        self._id = track_info.id
        self._parent = parent
        self._controller = controller
        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)
        self.processors = {}
        self._create_processors(track_info)
        self._create_common_controls(track_info)
        self._connect_signals()

    def create_processor(self, proc_info: sushi.ProcessorInfo) -> None:
        if proc_info.id not in self.processors:
            processor = ProcessorWidget(self._controller, proc_info, self._id, self)
            self._proc_layout.insertWidget(self._proc_layout.count() - 1, processor)
            self.processors[proc_info.id] = processor

    def _create_processors(self, track_info: sushi.TrackInfo) -> None:
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

        processors = self._controller.audio_graph.get_track_processors(track_info.id)
        for p in processors:
            processor = ProcessorWidget(self._controller, p, track_info.id, self)
            self._proc_layout.addWidget(processor, 0)
            self.processors[p.id] = processor

        self._proc_layout.addStretch()

    def _create_common_controls(self, track_info: sushi.TrackInfo) -> None:
        pan_gain_layout = QHBoxLayout(self)
        pan_gain_layout.setContentsMargins(0,0,0,0)
        pan_gain_box = QGroupBox('Master', self)
        pan_gain_box.setMaximumHeight(220)
        pan_gain_box.setLayout(pan_gain_layout)
        self._layout.addWidget(pan_gain_box)
        self._pan_gain = [PanGainWidget(self._id, 'Main Bus', 0, 1, self._controller, self)]
        pan_gain_layout.addWidget(self._pan_gain[0], 0, Qt.AlignLeft)

        # Create 1 pan/gain control per extra output bus
        for bus in range(1, track_info.buses):
            gain_id = self._controller.parameters.get_parameter_id(track_info.id, 'gain_sub_' + str(bus))
            pan_id = self._controller.parameters.get_parameter_id(track_info.id, 'pan_sub_' + str(bus))
            pan_gain = PanGainWidget(self._id, 'Sub Bus ' + str(bus), gain_id, pan_id, self._controller, self)
            pan_gain_layout.addWidget(pan_gain)
            self._pan_gain.append(pan_gain)

        self._track_buttons = QHBoxLayout(self)
        self._layout.addLayout(self._track_buttons)
        
        self._mute_button = QPushButton('Mute', self)
        self._track_buttons.addWidget(self._mute_button)
        self._mute_button.setCheckable(True)
        self._mute_id = self._controller.parameters.get_parameter_id(track_info.id, 'mute')
        self._mute_button.setChecked(self._controller.parameters.get_parameter_value(self._id, self._mute_id) == 1)

        self._delete_button = QPushButton('Delete', self)
        self._track_buttons.addWidget(self._delete_button)
        self._add_plugin_button = QPushButton('Add Plugin', self)
        self._track_buttons.addWidget(self._add_plugin_button)
        self._track_buttons.addStretch(0)

    def _connect_signals(self) -> None:
        self._mute_button.clicked.connect(self.mute_track)
        self._delete_button.clicked.connect(self.delete_track)
        self._add_plugin_button.clicked.connect(self.add_plugin)

    def handle_parameter_notification(self, notif: sushi.ParameterInfo) -> None:
        for pan_gain in self._pan_gain:
            if notif.parameter.parameter_id == pan_gain.pan_id:
                pan_gain.set_pan_slider(notif.normalized_value)
                pan_gain.set_pan_label(notif.formatted_value)

            elif notif.parameter.parameter_id == pan_gain.gain_id:
                pan_gain.set_gain_slider(notif.normalized_value)
                pan_gain.set_gain_label(notif.formatted_value)

        if notif.parameter.parameter_id == self._mute_id:
            self._mute_button.blockSignals(True)
            self._mute_button.setChecked(True if notif.normalized_value > 0.5 else False)
            self._mute_button.blockSignals(False)

    def mute_track(self, arg) -> None:
        state = self._mute_button.isChecked()
        muted = self._controller.parameters.set_parameter_value(self._id, self._mute_id, 1 if state == True else 0)

    def delete_track(self, arg) -> None:
        self._controller.audio_graph.delete_track(self._id)

    def add_plugin(self, arg):
        self._controller.add_plugin(self._id)

    def delete_processor(self, processor_id: int) -> None:
        p = self.processors.pop(processor_id)
        p.deleteLater() # Otherwise traces are left hanging
        self._proc_layout.removeWidget(p)

    def move_processor(self, processor_id: int, direction: sushi.IntEnum) -> None:
        p = self.processors[processor_id]
        index = self._proc_layout.indexOf(p)
        
        if direction == Direction.UP and index > 0:
            self._proc_layout.removeWidget(p)
            self._proc_layout.insertWidget(index - 1, p)

        # There is a 'hidden' stretch element that should always remain at the end
        # for layout purposes, so never move the processor past that element.
        elif direction == Direction.DOWN and index < self._proc_layout.count() - 2:
            self._proc_layout.removeWidget(p)
            self._proc_layout.insertWidget(index + 1, p)


class ProcessorWidget(QGroupBox):
    def __init__(self, controller: SushiController, processor_info: sushi.ProcessorInfo, track_id: int, parent: QWidget) -> None:
        super().__init__(processor_info.name, parent)
        self.setFixedWidth(PROCESSOR_WIDTH * MAX_COLUMNS)
        # Make sure the ProcessorWidget doesn't expand to much, as that looks ugly
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self._controller = controller
        self._id = processor_info.id
        self._track_id = track_id
        self._parameters = {}
        self._properties = {}
        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)

        self._create_common_controls(processor_info)
        self._create_parameters()
        self._create_properties()
        self._connect_signals()

    def _create_parameters(self) -> None:
        parameters = self._controller.parameters.get_processor_parameters(self._id)
        param_count = len(parameters)
        param_layout = QHBoxLayout()
        self._layout.addLayout(param_layout)
        for col in range(0, MAX_COLUMNS):
            col_layout = QVBoxLayout()
            param_layout.addLayout(col_layout)
            for p in parameters[col::MAX_COLUMNS]:
                parameter = ParameterWidget(p, self._id, self._controller, self)
                col_layout.addWidget(parameter)
                self._parameters[p.id] = parameter

            col_layout.addStretch()
        self._layout.addStretch()

    def _create_properties(self) -> None:
        properties = self._controller.parameters.get_processor_properties(self._id)
        prop_count = len(properties)
        prop_layout = QVBoxLayout()
        self._layout.addLayout(prop_layout)

        for p in properties:
            property = PropertyWidget(p, self._id, self._controller, self)
            prop_layout.addWidget(property)
            self._properties[p.id] = property

        self._layout.addStretch()

    def _create_common_controls(self, processor_info: sushi.ProcessorInfo) -> None:
        common_layout = QHBoxLayout(self)
        self._layout.addLayout(common_layout)

        self._mute_button = QPushButton(self)
        self._mute_button.setCheckable(True)
        self._mute_button.setChecked(self._controller.audio_graph.get_processor_bypass_state(self._id))
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
            for program in self._controller.programs.get_processor_programs(self._id):
                self._program_selector.addItem(program.name)
            current_program =self._controller.programs.get_processor_current_program(self._id)
            self._program_selector.setCurrentIndex(current_program)
            
        else:
            self._program_selector.addItem('No programs')
    
    def _connect_signals(self) -> None:
        self._mute_button.clicked.connect(self.mute_processor_clicked)
        self._program_selector.currentIndexChanged.connect(self.program_selector_changed)
        self._delete_button.clicked.connect(self.delete_processor_clicked)
        self._up_button.clicked.connect(self.up_clicked)
        self._down_button.clicked.connect(self.down_clicked)

    def handle_parameter_notification(self, notif: sushi.ParameterInfo) -> None:
        self._parameters[notif.parameter.parameter_id].set_slider_value(notif.normalized_value)
        self._parameters[notif.parameter.parameter_id].set_label_value(notif.formatted_value)

    def handle_property_notification(self, notif: sushi.PropertyInfo) -> None:
        self._properties[notif.property.property_id].set_value(notif.value)

    def delete_processor_clicked(self) -> None:
        self._controller.delete_processor(self._track_id, self._id)

    def up_clicked(self) -> None:
        self._controller.move_processor(self._track_id, self._id, Direction.UP)

    def down_clicked(self) -> None:
        self._controller.move_processor(self._track_id, self._id, Direction.DOWN)

    def mute_processor_clicked(self, arg) -> None:
        state = self._mute_button.isChecked()
        self._controller.audio_graph.set_processor_bypass_state(self._id, state)        

    def program_selector_changed(self, program_id: int) -> None:
        self._controller.programs.set_processor_program(self._id, program_id)


class ParameterWidget(QWidget):
    def __init__(self, parameter_info: sushi.ParameterInfo, processor_id: int, controller: SushiController, parent: QWidget) -> None:
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
        self._layout.setContentsMargins(0, 0, 0, 0)

        value = self._controller.parameters.get_parameter_value(self._processor_id, self._id)
        self.set_slider_value(value)
        txt_value = self._controller.parameters.get_parameter_value_as_string(self._processor_id, self._id)
        self.set_label_value(txt_value)

        if parameter_info.automatable:
            self._connect_signals()
        else:
            # It an output only parameter, it's not meant to be set by the user
            self._value_slider.setEnabled(False)

    def _connect_signals(self) -> None:
        self._value_slider.valueChanged.connect(self.value_changed)

    def value_changed(self) -> None:
        value = float(self._value_slider.value()) / SLIDER_MAX_VALUE
        self._controller.parameters.set_parameter_value(self._processor_id, self._id, value)

    def set_slider_value(self, value: float) -> None:
        ## Set value without triggering a signal
        self._value_slider.blockSignals(True)
        self._value_slider.setValue(value * SLIDER_MAX_VALUE)
        self._value_slider.blockSignals(False)

    def set_label_value(self, value: str) -> None:
        self._value_label.setText(value + ' ' + self._unit)


class PropertyWidget(QWidget):
    def __init__(self, property_info: sushi.PropertyInfo, processor_id: int, controller: 'SushiController' , parent: QWidget) -> None:
        super().__init__(parent)
        self._controller = controller
        self._id = property_info.id
        self._processor_id = processor_id
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)

        self._name_label = QLabel(property_info.name, self)
        self._name_label.setFixedWidth(PARAMETER_VALUE_WIDTH)
        self._layout.addWidget(self._name_label)

        self._edit_box = QLineEdit(self)
        self._layout.addWidget(self._edit_box)

        self._file_button = QPushButton('', self)
        self._file_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirIcon')))
        self._file_button.setToolTip("Set to a file location")
        self._layout.addWidget(self._file_button)
        self._file_button.clicked.connect(self.open_file_dialog)

        self._layout.setContentsMargins(0,0,0,0)

        value = self._controller.parameters.get_property_value(self._processor_id, self._id)
        self._edit_box.setText(value)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._edit_box.returnPressed.connect(self.value_changed)

    def value_changed(self) -> None:
        value = self._edit_box.text()
        self._controller.parameters.set_property_value(self._processor_id, self._id, value)

    def set_value(self, value: str) -> None:
        self._edit_box.blockSignals(True)
        self._edit_box.setText(value)
        self._edit_box.blockSignals(False)

    def open_file_dialog(self) -> None:
        dialog = QFileDialog(self)
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            self._edit_box.setText(filename)
            self._controller.parameters.set_property_value(self._processor_id, self._id, filename)


class PanGainWidget(QWidget):
    def __init__(self, processor_id: int, name: str, gain_id: int, pan_id: int, controller: 'SushiController', parent: QWidget) -> None:
        super().__init__(parent)
        self._processor_id = processor_id
        self.gain_id = gain_id
        self.pan_id = pan_id
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

        value = self._controller.parameters.get_parameter_value(self._processor_id, pan_id)
        self.set_pan_slider(value)
        txt_value = self._controller.parameters.get_parameter_value_as_string(self._processor_id, self.pan_id)
        self.set_pan_label(txt_value)

        value = self._controller.parameters.get_parameter_value(self._processor_id, gain_id)
        self.set_gain_slider(value)
        txt_value = self._controller.parameters.get_parameter_value_as_string(self._processor_id, self.gain_id)
        self.set_gain_label(txt_value)
        
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._pan_slider.valueChanged.connect(self.pan_changed)
        self._gain_slider.valueChanged.connect(self.gain_changed)

    def pan_changed(self) -> None:
        value = float(self._pan_slider.value()) / SLIDER_MAX_VALUE
        self._controller.parameters.set_parameter_value(self._processor_id, self.pan_id, value)

    def gain_changed(self) -> None:
        value = float(self._gain_slider.value()) / SLIDER_MAX_VALUE
        self._controller.parameters.set_parameter_value(self._processor_id, self.gain_id, value)

    def set_pan_slider(self, value: float) -> None:
        self._pan_slider.blockSignals(True)
        self._pan_slider.setValue(value * SLIDER_MAX_VALUE)
        self._pan_slider.blockSignals(False)

    def set_pan_label(self, txt_value: str) -> None:
        self._pan_label.setText(txt_value)

    def set_gain_slider(self, value: float) -> None:
        self._gain_slider.blockSignals(True)
        self._gain_slider.setValue(value * SLIDER_MAX_VALUE)
        self._gain_slider.blockSignals(False)

    def set_gain_label(self, txt_value: str) -> None:
        self._gain_label.setText(txt_value + ' ' + 'dB')
