# QT UI (deprecated)
Generic GUI for controlling Sushi over gRPC, built with python and QT. Can control both local instances and remote devices. Intended for testing and development.

## Usage

    $ python3 ./qt_client.py

## Dependencies
  * grpc-tools
  * protobuf
  * PySide2

Make sure to set the path to Sushis protofile before. If controlling Sushi on a remote device, change the ip from localhost to the ip of the elk device.

# TK UI (deprecated)
Generic GUI for controlling Sushi over gRPC, built with python and Tk. Can control both local instances and remote devices. Intended for testing and development and not for externa use. UI is very ugly and the code not up to standard for publishing.

Only works with Sushi version <= 0.9, use QT UI with more recent versions of Sushi

## Usage

	$ python3 ./client.py

Make sure to set the path to Sushis protofile before. If controlling Sushi on a remote device, change the ip from localhost to the ip of the elk device.