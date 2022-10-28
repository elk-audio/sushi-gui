import sys
import os

from PySide6.QtWidgets import QApplication

from elkpy import grpc_gen

from controller import Controller
from main_window import MainWindow 

from pathlib import Path

# If sushi is running on another device replace 'localhost' with the ip of that device 
SUSHI_ADDRESS = ('localhost:51051')

# Get protofile to generate grpc library
proto_file = os.environ.get('SUSHI_GRPC_ELKPY_PROTO')
if proto_file is None:
    print('Environment variable SUSHI_GRPC_ELKPY_PROTO not defined, set it to point the .proto definition')
    sys.exit(-1)

# Get the sushi notification types direcly from the generated grpc types
sushi_grpc_types, _ = grpc_gen.modules_from_proto(proto_file)

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
