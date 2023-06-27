from enum import IntEnum

SYNCMODES = ['Internal', 'Midi', 'Link']
PLUGIN_TYPES = ['Internal', 'Vst2x', 'Vst3x', 'LV2']
MODE_PLAYING = 2

# Number of columns of parameters to display per processor
# 1-3 works reasonably well
MAX_COLUMNS = 1

# Gui size constants
PROCESSOR_WIDTH = 300
PARAMETER_VALUE_WIDTH = 80
ICON_BUTTON_WIDTH = 30
SLIDER_HEIGHT = 15
SLIDER_MIN_WIDTH = 100
PAN_SLIDER_WIDTH = 60
FILE_BUTTON_WIDTH = 40

# Slider values are ints in QT, so we need to scale with an integer factor to get 0-1 floats
SLIDER_MAX_VALUE = 1024


# Convenience enum
class Direction(IntEnum):
    UP = 1
    DOWN = 2
