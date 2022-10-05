# QT UI
A generic GUI for controlling Sushi over gRPC, built with python and QT.
It can control both local instances and remote devices. 
Intended for testing and development.

## Usage

    $ python3 ./qt_client.py

## Dependencies
  * grpc-tools >= 1.29
  * protobuf
  * PySide2
  * elkpy

## Notes
* Make sure to set the path to Sushi's `.proto` definition file _sushi_rpc.proto_ file before launching, by setting the 
  environment variable `SUSHI_GRPC_ELKPY_PROTO` to it.
* If controlling Sushi running on a remote device, change the ip from localhost to the *ip of the elk device*.
* It is assumed that you have copied the ElkPy package to the UI top directory, as advised in the ElkPy documentation. 
If you want to use ElkPy from another place, do not forget to adapt the relevant `import` statements. 

## Usage
```
$ export SUSHI_GRPC_ELKPY_PROTO=./sushi_rpc.proto
$ python3 ./client.py
```

Make sure to set the path to _sushi_rpc.proto_ before launching.
If controlling Sushi running on a remote device, change the ip from localhost to the ip of the elk device.