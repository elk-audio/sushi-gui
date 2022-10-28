import os
from enum import IntEnum
from elkpy import grpc_gen


# If sushi is running on another device replace 'localhost' with the ip of that device 
SUSHI_ADDRESS = ('localhost:51051')

SYNCMODES = ['Internal', 'Midi', 'Link']
PLUGIN_TYPES = ['Internal', 'Vst2x', 'Vst3x', 'LV2']
MODE_PLAYING = 2

# Number of columns of parameters to display per processor
# 1-3 works reasonably well
MAX_COLUMNS              = 1

# Gui size constants
PROCESSOR_WIDTH          = 300
PARAMETER_VALUE_WIDTH    = 80
ICON_BUTTON_WIDTH        = 30
SLIDER_HEIGHT            = 15
SLIDER_MIN_WIDTH         = 100
PAN_SLIDER_WIDTH         = 60
FILE_BUTTON_WIDTH        = 40

# Slider values are ints in QT, so we need to scale with an integer factor to get 0-1 floats
SLIDER_MAX_VALUE         = 1024

# Convenience enum
class Direction(IntEnum):
    UP = 1
    DOWN = 2

# Get protofile to generate grpc library
proto_file = os.environ.get('SUSHI_GRPC_ELKPY_PROTO')
if proto_file is None:
    print('Environment variable SUSHI_GRPC_ELKPY_PROTO not defined, set it to point the .proto definition')
    sys.exit(-1)

# Get the sushi notification types direcly from the generated grpc types
sushi_grpc_types, _ = grpc_gen.modules_from_proto(proto_file)