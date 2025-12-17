#! /usr/local/bin/python3

import sys
import argparse
from PySide6.QtWidgets import QApplication
from sushi_gui import load_plugins_file
from sushi_gui.main_window import MainWindow


# If sushi is running on another device replace 'localhost' with the ip of that device
SUSHI_ADDRESS = 'localhost:51051'
if sys.platform == 'win32':
    SUSHI_ADDRESS = 'localhost:510'


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='SUSHI GUI - A GUI for controlling Sushi over gRPC'
    )
    parser.add_argument(
        '--plugins-file',
        type=str,
        default=None,
        help='Path to custom plugins JSON file (default: installed_plugins.json in repo root)'
    )
    parser.add_argument(
        '--address',
        type=str,
        default=SUSHI_ADDRESS,
        help=f'Sushi address in format host:port (default: {SUSHI_ADDRESS})'
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load plugins file if custom path provided
    if args.plugins_file:
        load_plugins_file(args.plugins_file)

    # Create Qt application
    # Note: QApplication needs to be created with sys.argv, but we've already parsed args
    # so we pass the original sys.argv to QApplication
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    window = MainWindow(sushi_address=args.address)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
