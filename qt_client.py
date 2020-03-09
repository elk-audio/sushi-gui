import os
from time import sleep
import threading
from elkpy import sushicontroller as sc
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

MAX_PARAMETERS_IN_COLUMN = 14
SLIDER_HEIGHT            = 15
SLIDER_MIN_WIDTH         = 100
# Slider values are ints in QT
SLIDER_MAX_VALUE         = 1024


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self._sushi = controller
        self.setWindowTitle('Sushi')
        ##self.setFixedSize(235, 235)
        # Set the central widget and the general layout
        self._window_layout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self._window_layout)
        self._tpbar = TransportBarWidget(self._sushi)
        self._window_layout.addWidget(self._tpbar)
        self._tracks = []
        self._create_tracks()

    def _create_tracks(self):
        self._track_layout = QHBoxLayout(self)
        self._window_layout.addLayout(self._track_layout)
        tracks = self._sushi.get_tracks()
        for t in tracks:
            track = TrackWidget(self._sushi, t, self)
            self._track_layout.addWidget(track)
            self._tracks.append(track)

class TransportBarWidget(QGroupBox):
    def __init__(self, controller):
        super().__init__()
        self._sushi = controller
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
        self._layout.addWidget(self._tempo)
        self._play_button = QPushButton("Play", self)
        self._layout.addWidget(self._play_button)
        self._stop_button = QPushButton("Stop", self)
        self._layout.addWidget(self._stop_button)
        self._layout.addStretch(0)


    def _connect_signals(self):
        pass

class TrackWidget(QGroupBox):
    def __init__(self, controller, track_info, parent):
        super().__init__(track_info.name, parent)
        self._id = track_info.id
        self._sushi = controller
        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)
        self._processors = []
        self._create_processors(track_info)
        self._create_common_controls()

    def _create_processors(self, track_info):
        processors = self._sushi.get_track_processors(track_info.id)
        for p in processors:
            processor = ProcessorWidget(self._sushi, p, self)
            self._layout.addWidget(processor)
            self._processors.append(processor)

    def _create_common_controls(self):
        self._pan_gain = PanGainWidget(self._sushi, self)
        self._layout.addWidget(self._pan_gain)
        self._track_buttons = QHBoxLayout(self)
        self._layout.addLayout(self._track_buttons)
        self._mute_button = QPushButton("Mute", self)
        self._track_buttons.addWidget(self._mute_button)
        self._delete_button = QPushButton("Delete", self)
        self._track_buttons.addWidget(self._delete_button)


class ProcessorWidget(QGroupBox):
    def __init__(self, controller, processor_info, parent):
        super().__init__(processor_info.name)
        self._sushi = controller
        self._id = processor_info.id
        self._parameters = []
        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)
        self._create_parameters()
        if processor_info.program_count > 0:
            self._create_program_selector()

        else:
            label = QLabel("Plugin doesn't have any programs", self)
            self._layout.addWidget(label)

    def _create_parameters(self):
        parameters = self._sushi.get_processor_parameters(self._id)
        columns = int(len(parameters) / MAX_PARAMETERS_IN_COLUMN) + 1
        param_layout = QHBoxLayout()
        self._layout.addLayout(param_layout)
        for col in range(0, columns):
            col_layout = QVBoxLayout()
            param_layout.addLayout(col_layout)
            #param_layout.setContentsMargins(0,0,0,0)
            for p in parameters[col * MAX_PARAMETERS_IN_COLUMN: (col + 1)  * (MAX_PARAMETERS_IN_COLUMN)]:
                parameter = ParameterWidget(p, self._id, self._sushi, self)
                #parameter.setContentsMargins(0,0,0,0)
                col_layout.addWidget(parameter)
                self._parameters.append(parameter)

            col_layout.addStretch()
        self._layout.addStretch()

    def _create_program_selector(self):
        program_layout = QHBoxLayout(self)
        self._layout.addLayout(program_layout)
        programs = self._sushi.get_processor_programs(self._id)
        label = QLabel("Program", self)
        program_layout.addWidget(label)
        self._program_selector = QComboBox(self)
        program_layout.addWidget(self._program_selector)
        program_layout.addStretch(0)
        for program in programs:
            self._program_selector.addItem(program.name)


class ParameterWidget(QWidget):
    def __init__(self, parameter_info, processor_id, controller, parent):
        super().__init__(parent)
        self._sushi = controller
        self._id = parameter_info.id
        self._processor_id = processor_id
        self._unit = parameter_info.unit
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)
        self._name_label = QLabel(parameter_info.name, self)
        self._name_label.setFixedSize(80, SLIDER_HEIGHT)
        self._layout.addWidget(self._name_label)
        self._value_slider = QSlider(Qt.Orientation.Horizontal, self)
        self._value_slider.setFixedSize(SLIDER_MIN_WIDTH, SLIDER_HEIGHT)
        self._value_slider.setRange(0, SLIDER_MAX_VALUE)
        self._layout.addWidget(self._value_slider)
        self._value_label = QLabel("0.0" + parameter_info.unit, self)
        self._value_label.setFixedSize(60, SLIDER_HEIGHT)
        self._value_label.setAlignment(Qt.AlignRight)
        self._layout.addWidget(self._value_label)
        self._layout.setContentsMargins(0,0,0,0)
        self.update()
        self._connect_signals()

    def _connect_signals(self):
        self._value_slider.valueChanged.connect(self.value_changed)

    def update(self):
        value = self._sushi.get_parameter_value(self._processor_id, self._id)
        self._value_slider.setValue(value * SLIDER_MAX_VALUE)
        txt_value = self._sushi.get_parameter_value_as_string(self._processor_id, self._id)
        self._value_label.setText(txt_value + " " + self._unit)

    def value_changed(self):
        value = float(self._value_slider.value()) / SLIDER_MAX_VALUE
        self._sushi.set_parameter_value(self._processor_id, self._id, value)
        txt_value = self._sushi.get_parameter_value_as_string(self._processor_id, self._id)
        self._value_label.setText(txt_value + " " + self._unit)

class PanGainWidget(QWidget):
    def __init__(self, processor_id, parent):
        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._layout.setSpacing(0)
        pan_label = QLabel("Pan", self)
        self._layout.addWidget(pan_label, 0, 0)
        gain_label = QLabel("Gain", self)
        self._layout.addWidget(gain_label, 0, 1)
        self._pan_dial = QDial(self)
        self._pan_dial.setFixedHeight(40)
        self._pan_dial.setRange(0, SLIDER_MAX_VALUE)
        self._pan_dial.setValue(SLIDER_MAX_VALUE / 2)
        self._pan_dial.setContentsMargins(0,0,0,0)
        self._layout.addWidget(self._pan_dial, 1, 0)
        self._gain_slider = QSlider(Qt.Orientation.Vertical, self)
        self._gain_slider.setFixedHeight(80)
        self._layout.addWidget(self._gain_slider, 1, 1)
        self._pan_value_label = QLabel("0,0")
        self._layout.addWidget(self._pan_value_label, 2, 0)
        self._gain_value_label = QLabel("0,0")
        self._layout.addWidget(self._gain_value_label, 2, 1)
        self._layout.setAlignment(Qt.AlignHCenter)

        #self._layout.setAlignment(Qt.AlignHCenter)
        #self._layout.setAlignment(self._pan_dial, Qt.AlignRight)
        #   self._layout.setAlignment(self._gain_slider, Qt.AlignHCenter)



# Create a Controller class to connect the GUI and the model
class PyCalcCtrl:
    """PyCalc's Controller."""
    def __init__(self, model, view):
        """Controller initializer."""
        self._evaluate = model
        self._view = view
        # Connect signals and slots
        self._connectSignals()

    def _calculateResult(self):
        """Evaluate expressions."""
        result = self._evaluate(expression=self._view.displayText())
        self._view.setDisplayText(result)

    def _buildExpression(self, sub_exp):
        """Build expression."""
        if self._view.displayText() == ERROR_MSG:
            self._view.clearDisplay()

        expression = self._view.displayText() + sub_exp
        self._view.setDisplayText(expression)

    def _connectSignals(self):
        """Connect signals and slots."""
        for btnText, btn in self._view.buttons.items():
            if btnText not in {'=', 'C'}:
                btn.clicked.connect(partial(self._buildExpression, btnText))

        self._view.buttons['='].clicked.connect(self._calculateResult)
        self._view.display.returnPressed.connect(self._calculateResult)
        self._view.buttons['C'].clicked.connect(self._view.clearDisplay)

# Create a Model to handle the calculator's operation
def evaluateExpression(expression):
    """Evaluate an expression."""
    try:
        result = str(eval(expression, {}, {}))
    except Exception:
        result = ERROR_MSG

    return result

# Client code
def main():
    app = QApplication(sys.argv)
    controller = sc.SushiController(SUSHI_ADDRESS, proto_file)
    window = MainWindow(controller)
    window.show()
    # Create instances of the model and the sushi
    model = evaluateExpression
    #PyCalcCtrl(model=model, view=view)
    # Execute calculator's main loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()