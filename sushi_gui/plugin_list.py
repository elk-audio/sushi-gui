import json


PLUGIN_JSON = 'sushi_gui/plugins.json'


with open(PLUGIN_JSON, "r") as f:
    PLUGIN_DICT = json.loads(f.read())  

