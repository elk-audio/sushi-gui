#! /usr/local/bin/python3

import sys
from PySide6.QtWidgets import QApplication
from sushi_gui.main_window import MainWindow


# If sushi is running on another device replace 'localhost' with the ip of that device 
SUSHI_ADDRESS = 'localhost:51051'


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow(sushi_address=SUSHI_ADDRESS)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
