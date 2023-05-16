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

### Sushi .proto definitions
In the Sushi repo, you will find the `.proto` definition file for Sushi. Specifically in `sushi/rpc_interface/protos/sushi_rpc.proto`

You need to set an environment variable to that:
```
$ export SUSHI_GRPC_ELKPY_PROTO=path_to_sushi/rpc_interface/protos/sushi_rpc.proto
```

If you find yourself using is often and wanting to set the variable *once and for all*, you should add the command to your
`.bashrc` or `.zshrc`, depending on which shell you are using.

For convenience, we added a copy of `sushi_rpc.proto` to this repo that `client.py` will default to using in case the
env variable is not set. Be aware that this is not the preferred method as we cannot guarantee regular updates to 
this copy. Using the actual proto file that comes with Sushi will always ensure best compatibility and latest features.

---


## Usage

    $ python3 ./client.py

## Controlling Sushi when it is running on another machine
To achieve this, you need at least 2 things:
- The `sushi_rpc.proto` file. This is required but you don't need Sushi itself. You could in principle get that file only, 
store it locally and set SUSHI_GRPC_ELKPY_PROTO to it. Feel free to use the included copy of `sushi_rpc.proto` but do
remember that it might not be 100% up-to-date.
- The IP address of the machine running the Sushi instance you want to control. Replace `localhost` with it in `client.py` but keep the port number:

```
SUSHI_ADDRESS = 'localhost:51051'
```
becomes
```
SUSHI_ADDRESS = 'sushi_current_ip_address:51051'
```

## Limitations
Although meant as a debugging/testing tools for Sushi developers, this GUI does **not** implement all of Sushi's features.
Most notably, some behavior one might expect after learning about the notification system is missing:

### Processor update notifications and ordering
Sushi allows for adding processor anywhere in the processor stack. But this GUI does not. When adding a plugin, it will
always add it at the bottom of the stack, i.e. in the last position in the audio flow. This limitation gets even more
annoying when the processor addition is done via other means which do allow for insertion in any position because this 
GUI will **not** reflect the new ordering: the new plugin will always be shown at the bottom of the stack even though
it is actually somewhere else. Keep that in mind.

---



## Packaging the GUI app with PyInstaller
The repo contains a `client.spec` file. This is a specification file to be used by PyInstaller that will produce a bundled executable app named `sushi_gui`.

With the venv **activated**:
```
pip install pyinstaller 
pyinstaller client.spec
```
You will find a folder called `client` in `dist/`. This can be zipped and distributed. Inside that folder is `sushi_gui` that can be executed without **any** of the installation steps
described above, except for 1 limitation:
- The controlled Sushi instance MUST be on the same machine

## Dependency list
  * grpcio 
  * grpc-tools
  * PySide6
  * elkpy
