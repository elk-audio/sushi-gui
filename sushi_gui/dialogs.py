from typing import Optional, TYPE_CHECKING
from functools import partial

from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDialogButtonBox,
    QPushButton,
    QMenu,
)
from sushi_gui import INSTALLED_PLUGINS

if TYPE_CHECKING:
    from sushi_gui.main_window import MainWindow

from .constants import PLUGIN_TYPES
from elkpy import sushi_info_types as sushi


class AddTrackDialog(QDialog):
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Add new track")

        self._layout: QGridLayout = QGridLayout(self)
        self.setLayout(self._layout)

        self.name_label = QLabel("Name", self)
        self._layout.addWidget(self.name_label, 0, 0)
        self._name_entry = QLineEdit(self)
        self._layout.addWidget(self._name_entry, 0, 1)

        nr_of_channels = QLabel("Track type:")
        self._layout.addWidget(nr_of_channels, 2, 0)
        self._track_type = QComboBox(self)
        self._track_type.addItem("Mono")
        self._track_type.addItem("Stereo")
        self._track_type.addItem("Multibus")
        self._track_type.setCurrentIndex(1)
        self._layout.addWidget(self._track_type, 2, 1)

        self._inputs_lbl = QLabel("Inputs:")
        self._inputs_sb = QSpinBox()
        self._inputs_sb.setMinimum(1)
        self._inputs_sb.setMaximum(8)
        self._layout.addWidget(self._inputs_lbl, 3, 0)
        self._layout.addWidget(self._inputs_sb, 3, 1)
        self._inputs_lbl.hide()
        self._inputs_sb.hide()

        self._outputs_lbl = QLabel("Outputs:")
        self._outputs_lbl.hide()
        self._outputs_sb = QSpinBox()
        self._outputs_sb.hide()
        self._outputs_sb.setMinimum(1)
        self._outputs_sb.setMaximum(8)
        self._layout.addWidget(self._outputs_lbl, 4, 0)
        self._layout.addWidget(self._outputs_sb, 4, 1)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setDefault(True)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._layout.addWidget(self.button_box, 5, 1)

        self._connect_signals()

    @property
    def track_type(self) -> QComboBox:
        return self._track_type

    @property
    def inputs_sb(self) -> QSpinBox:
        return self._inputs_sb

    @property
    def outputs_sb(self) -> QSpinBox:
        return self._outputs_sb

    @property
    def name_entry(self) -> QLineEdit:
        return self._name_entry

    def _connect_signals(self) -> None:
        self._track_type.currentIndexChanged.connect(self._update_nr_of_channels)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def _update_nr_of_channels(self, idx: int) -> None:
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
    """This dialog adds Sushi Internal plugins only. It presents them as a categorized menu."""

    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)
        self.setWindowTitle("Add new plugin")

        self._layout = QGridLayout(self)
        self.setLayout(self._layout)

        # Store the selected plugin data
        self._selected_plugin = None
        self._selected_plugin_name = None

        # Store submenu references to prevent Qt from deleting them
        self._category_menus = []
        self._subcategory_menus = []

        name_label = QLabel("Name", self)
        self._layout.addWidget(name_label, 1, 0)
        self._name_entry = QLineEdit(self)
        self._name_entry.setMinimumWidth(200)
        self._layout.addWidget(self._name_entry, 1, 1)

        plug_lbl = QLabel("Plugin", self)
        self._layout.addWidget(plug_lbl, 4, 0)

        # Create button with menu for plugin selection
        self._plug_button = QPushButton("Select Plugin...", self)
        self._plug_button.setMinimumWidth(200)
        self._layout.addWidget(self._plug_button, 4, 1)

        # Create menu with categories
        self._plug_menu = QMenu(self)
        self._create_plugin_menu()
        self._plug_button.setMenu(self._plug_menu)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setDefault(True)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._layout.addWidget(self.button_box, 5, 1)

        self._connect_signals()

    def _create_plugin_menu(self) -> None:
        """Create 3-level hierarchical menu from plugin categories."""
        plugins_dict = INSTALLED_PLUGINS.get("plugins", {})

        # Level 1: Iterate over main categories (e.g., "Internal", "Brickworks")
        for category_name, subcategories in plugins_dict.items():
            # Create submenu for this main category
            category_menu = self._plug_menu.addMenu(category_name)
            # Store reference to prevent Qt from deleting it
            self._category_menus.append(category_menu)

            # Level 2: Iterate over subcategories (e.g., "Utility", "EQ", "Generator")
            if isinstance(subcategories, dict):
                for subcategory_name, plugins in subcategories.items():
                    # Create submenu for this subcategory
                    subcategory_menu = category_menu.addMenu(subcategory_name)
                    # Store reference to prevent Qt from deleting it
                    self._subcategory_menus.append(subcategory_menu)

                    # Level 3: Add each plugin as an action in the subcategory submenu
                    if isinstance(plugins, dict):
                        for plugin_key, plugin_data in plugins.items():
                            action = subcategory_menu.addAction(plugin_key)
                            # Store plugin data with the action
                            action.setData({"key": plugin_key, "data": plugin_data})
                            # Use functools.partial to properly capture the action in the closure
                            action.triggered.connect(partial(self._plugin_selected, action))

    def _plugin_selected(self, action) -> None:
        """Handle plugin selection from menu."""
        action_data = action.data()
        self._selected_plugin = action_data["data"]
        self._selected_plugin_name = action_data["key"]

        # Update button text to show selection
        self._plug_button.setText(self._selected_plugin_name)

        # Auto-fill name field if empty
        if not self._name_entry.text():
            self._name_entry.setText(self._selected_plugin_name)

    @property
    def selected_plugin(self) -> dict:
        return self._selected_plugin

    @property
    def plugin_name(self) -> str:
        return self._name_entry.text()

    def _connect_signals(self) -> None:
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)


class AddCustomPluginDialog(QDialog):
    """This lets the user add any VST or LV2 plugin present on the system by specifying a path or uid."""

    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)
        self.setWindowTitle("Add custom plugin")

        self._layout = QGridLayout(self)
        self.setLayout(self._layout)

        self._type: Optional[sushi.PluginType] = None

        type_label = QLabel("Type", self)
        self._layout.addWidget(type_label, 0, 0)
        self._type_box = QComboBox(self)
        self._layout.addWidget(self._type_box, 0, 1)
        for t in PLUGIN_TYPES:
            self._type_box.addItem(t)

        name_label = QLabel("Name", self)
        self._layout.addWidget(name_label, 1, 0)
        self._name_entry = QLineEdit(self)
        self._name_entry.setMinimumWidth(200)
        self._layout.addWidget(self._name_entry, 1, 1)

        self._uid_label = QLabel("Uid", self)
        self._layout.addWidget(self._uid_label, 2, 0)
        self._uid_entry = QLineEdit(self)
        self._layout.addWidget(self._uid_entry, 2, 1)

        self._path_label = QLabel("Path", self)
        self._layout.addWidget(self._path_label, 3, 0)
        self._path_entry = QLineEdit(self)
        self._path_entry.setEnabled(False)
        self._layout.addWidget(self._path_entry, 3, 1)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setDefault(True)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._layout.addWidget(self.button_box, 4, 1)

        self._connect_signals()

    @property
    def name_entry(self) -> QLineEdit:
        return self._name_entry

    @property
    def uid_entry(self) -> QLineEdit:
        return self._uid_entry

    @property
    def path_entry(self) -> QLineEdit:
        return self._path_entry

    @property
    def plugin_type(self) -> sushi.PluginType:
        return self._type

    @property
    def selected_plugin(self) -> dict:
        return self._plug_box.currentData()

    def _connect_signals(self) -> None:
        self._type_box.currentIndexChanged.connect(self.type_changed)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def type_changed(self, type_index: int) -> None:
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
