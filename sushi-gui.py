#! /usr/local/bin/python3

import sys
import json
from PySide6.QtWidgets import QApplication
from sushi_gui.main_window import MainWindow


# If sushi is running on another device replace 'localhost' with the ip of that device 
SUSHI_ADDRESS = 'localhost:51051'
PLUGIN_JSON = 'plugins.json'


def parse_plugin_list() -> dict:
    with open(PLUGIN_JSON, "r") as json_file:
        return json.loads(json_file.read())


def main():
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    plug_dict = parse_plugin_list()
    window = MainWindow(sushi_address=SUSHI_ADDRESS, plugins=plug_dict)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
