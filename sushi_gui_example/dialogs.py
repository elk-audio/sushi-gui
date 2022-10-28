from PySide6.QtWidgets import *

class AddTrackDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Add new track')

        self._layout = QGridLayout(self)
        self.setLayout(self._layout)

        self.name_label = QLabel('Name', self)
        self._layout.addWidget(self.name_label, 0,0)
        self._name_entry = QLineEdit(self)
        self._layout.addWidget(self._name_entry,0,1)

        nr_of_channels = QLabel('Track type:')
        self._layout.addWidget(nr_of_channels, 2, 0)
        self._track_type = QComboBox(self)
        self._track_type.addItem('Mono')
        self._track_type.addItem('Stereo')
        self._track_type.addItem('Multibus')
        self._track_type.setCurrentIndex(1)
        self._layout.addWidget(self._track_type, 2, 1)

        self._inputs_lbl = QLabel('Inputs:')
        self._inputs_sb = QSpinBox()
        self._inputs_sb.setMinimum(1)
        self._inputs_sb.setMaximum(8)
        self._layout.addWidget(self._inputs_lbl, 3, 0)
        self._layout.addWidget(self._inputs_sb, 3, 1)
        self._inputs_lbl.hide()
        self._inputs_sb.hide()

        self._outputs_lbl = QLabel('Outputs:')
        self._outputs_lbl.hide()
        self._outputs_sb = QSpinBox()
        self._outputs_sb.hide()
        self._outputs_sb.setMinimum(1)
        self._outputs_sb.setMaximum(8)
        self._layout.addWidget(self._outputs_lbl, 4, 0)
        self._layout.addWidget(self._outputs_sb, 4, 1)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setDefault(True)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._layout.addWidget(self.button_box, 5, 1)

        self._connect_signals()

    def _connect_signals(self):
        self._track_type.currentIndexChanged.connect(self._update_nr_of_channels)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def _update_nr_of_channels(self, idx: int):
        if idx == 2:
            self._inputs_sb.show()
            self._inputs_lbl.show()
            self._outputs_sb.show()
            self._outputs_lbl.show()
        else:
            self._inputs_sb.hide()
            self._inputs_lbl.hide()
            self._outputs_sb.hide()
            self._outputs_lbl.hide()


class AddPluginDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Add new plugin')

        self._layout = QGridLayout(self)
        self.setLayout(self._layout)

        self._type = None

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

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                               QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setDefault(True)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._layout.addWidget(self.button_box, 4, 1)
        
        self._connect_signals()

    def _connect_signals(self):
        self._type_box.currentIndexChanged.connect(self.type_changed)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def type_changed(self, type_index):
        plugin_type = type_index + 1
        self._type = plugin_type
        if plugin_type == sushi.PluginType.INTERNAL:
            self._path_entry.setEnabled(False)
            self._uid_entry.setEnabled(True)

        elif plugin_type == sushi.PluginType.VST2X:
            self._path_entry.setEnabled(True)
            self._uid_entry.setEnabled(False)

        elif plugin_type == sushi.PluginType.VST3X:
            self._path_entry.setEnabled(True)
            self._uid_entry.setEnabled(True)

        elif plugin_type == sushi.PluginType.LV2:
            self._path_entry.setEnabled(True)
            self._uid_entry.setEnabled(False)
