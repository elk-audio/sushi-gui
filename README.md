# QT UI
A generic GUI for controlling Sushi over gRPC, built with Python and QT.
It can control both local instances and remote devices. 
Intended for testing and development.

## Installation
It is assumed you have Python 3 on your system. And Sushi, of course...


### Dependencies
The preferred way to install deps is in a virtual environment. Here is how to do it with the builtin `venv` module. Using 
`virtualenv` instead is also possible.
- `python3 -m venv venv` will create a virtual environment named *venv* with your installed Python
- `source venv/bin/activate` to activate that environment
- `pip install -r requirements.txt` to install all the dependencies in the environment

### elkpy
At the time of writing, `elkpy` is not available on any package distribution platform (We are working on that...).
To install it, you will have to get it from our public repo and install it manually:
- get elkpy at `https://github.com/elk-audio/elkpy.git` 
- with the **activated** venv, `pip install -e path-to-elkpy` where you replaced *path-to-elkpy* with the actual path to the downloaded repo

You can confirm that it installed correctly by reading through the list returned by `pip list`.

### Sushi .proto definitions
In the Sushi repo, you will find the `.proto` definition file for Sushi. Specifically in `sushi/rpc_interface/protos/sushi_rpc.proto`

You need to set an environment variable to that:
```
$ export SUSHI_GRPC_ELKPY_PROTO=path_to_sushi/rpc_interface/protos/sushi_rpc.proto
```
Remember that the previous command sets the variable for the current shell session **only**. Therefore, you'll have to
repeat it every time you use this application.

If you find yourself using is often and wanting to set the variable *once and for all*, you should add the command to your
`.bashrc` or `.zshrc`, depending on which shell you are using.

## Usage

    $ python3 ./client.py

## Controlling Sushi when it is running on another machine
To achieve this, you need at least 2 things:
- The `sushi_rpc.proto` file. This is required but you don't need Sushi itself. You could in principle get that file only, store it locally and set SUSHI_GRPC_ELKPY_PROTO to it.
- The IP address of the machine running the Sushi instance you want to control. Replace `localhost` with it in `client.py` but keep the port number:

```
SUSHI_ADDRESS = 'localhost:51051'
```

## Dependency list
  * grpcio 
  * grpc-tools
  * protobuf
  * PySide6
  * elkpy
