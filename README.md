# QT UI
Generic GUI for controlling Sushi over gRPC, built with python and QT. Can control both local instances and remote devices. Intended for testing and development.

## Usage

    $ python3 ./qt_client.py

## Dependencies
  * grpc-tools >= 1.29
  * protobuf
  * PySide2

## Notes
* Make sure to set the path to _sushi_rpc.proto_ before launching. 
* If controlling Sushi running on a remote device, change the ip from localhost to the *ip of the elk device*.
* It is assumed that you have copied the ElkPy package to the UI top directory, as advised in the ElkPy documentation. 
If you want to use ElkPy from another place, do not forget to adapt the relevant `import` statements. 

# TK UI (deprecated)
`client.py` is a generic GUI for controlling Sushi over gRPC, built with python and Tk. Can control both local instances and remote devices. Intended for testing and development and not for externa use. UI is very ugly and the code not up to standard for publishing.

Only works with Sushi version <= 0.9, use QT UI with more recent versions of Sushi

## Usage

	$ python3 ./client.py

Make sure to set the path to _sushi_rpc.proto_ before launching. If controlling Sushi running on a remote device, change the ip from localhost to the ip of the elk device.