import os
import sys

from constants import *
from dialogs import *
from widgets import *
from controller import Controller
from main_window import MainWindow 

from pathlib import Path

# If sushi is running on another device replace 'localhost' with the ip of that device 
SUSHI_ADDRESS = ('localhost:51051')

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    controller = Controller(SUSHI_ADDRESS, proto_file)
    window = MainWindow(controller)
    window.show()
    controller.set_view(window)
    controller.subscribe_to_notifications()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
