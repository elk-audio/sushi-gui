# SUSHI GUI
A generic GUI for controlling Sushi over gRPC, built with Python and QT.
It can control both local instances and remote devices. 
Intended for testing and development.

## Installation
It is assumed you have Python 3 on your system. And Sushi, of course...

After cloning this repo, do not forget to run `git submodule update --init --recursive`! 
### Dependencies
The preferred way to install deps is in a virtual environment. Here is how to do it with the builtin `venv` module. Using 
`virtualenv` instead is also possible.
- `python3 -m venv venv` will create a virtual environment named *venv* with your installed Python
- `source venv/bin/activate` to activate that environment
- `pip install -r requirements.txt` to install all the dependencies in the environment

### Sushi .proto definitions
`sushi-grpc-api` is included in this repo as a submodule. It contains the proto definition file for Sushi.
In the Sushi repo, you will find the `.proto` definition file for Sushi. By default, this GUI will use that.

In case you need to use another proto file, you should set the environment variable SUSHI_GRPC_ELKPY_PROTO to that
path.

Also, note that Sushi comes with its proto file when you check it out. Specifically in `sushi/rpc_interface/protos/sushi_rpc.proto`.
So setting environment variable like that:
```
$ export SUSHI_GRPC_ELKPY_PROTO=path_to_sushi/rpc_interface/protos/sushi_rpc.proto
```
will make the GUI use the proto file included with Sushi.

If you find yourself using this often and wanting to set the variable *once and for all*, you should add the command to your
`.bashrc` or `.zshrc`, depending on which shell you are using.


---


## Usage
Assuming that Sushi is running on your machine:

    $ python3 ./client.py

## Controlling Sushi when it is running on another machine
The GUI lets you specify an IP address and port number to connect to. Simple as that.

In case you need to hard-code a different default address than `localhost:51051`, feel free
to edit `client.py:4`:
```
SUSHI_ADDRESS = 'localhost:51051'
```
with the new default address.

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
described above.

## Dependency list
  * grpcio 
  * grpc-tools
  * PySide6
  * elkpy
