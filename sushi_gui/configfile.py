from elkpy.sushicontroller import SushiController
from elkpy.sushi_info_types import PlayingMode, SyncMode, AudioConnection, TrackInfo
import json


DEFAULT_DUMPED_CONFIG_FILENAME = "config_dump.json"


class SessionState:
    """
    Class to represent the entire Sushi session"""

    sushi_info: dict = {}
    save_date: str = ""
    osc_state: dict = {}
    midi_state: dict = {}
    engine_state: dict = {}
    tracks: list = []

    def __init__(self, grpc_SessionState) -> None:
        s = grpc_SessionState
        self.sushi_info["version"] = s.sushi_info.version
        self.sushi_info["build_options"] = [
            option for option in s.sushi_info.build_options
        ]
        self.sushi_info["audio_buffer_size"] = s.sushi_info.audio_buffer_size
        self.sushi_info["commit_hash"] = s.sushi_info.commit_hash
        self.sushi_info["build_date"] = s.sushi_info.build_date

        self.save_date = s.save_date

        self.midi_state["inputs"] = s.midi_state.inputs
        self.midi_state["outputs"] = s.midi_state.outputs

        self.engine_state["sample_rate"] = s.engine_state.sample_rate
        self.engine_state["tempo"] = s.engine_state.tempo
        self.engine_state["playing_mode"] = PlayingMode(
            s.engine_state.playing_mode.mode
        ).name.lower()
        self.engine_state["sync_mode"] = SyncMode(
            s.engine_state.sync_mode.mode
        ).name.lower()
        self.engine_state["time_signature"] = {}
        self.engine_state["time_signature"]["numerator"] = (
            s.engine_state.time_signature.numerator
        )
        self.engine_state["time_signature"]["denominator"] = (
            s.engine_state.time_signature.denominator
        )
        self.engine_state["used_audio_inputs"] = s.engine_state.used_audio_inputs
        self.engine_state["used_audio_outputs"] = s.engine_state.used_audio_outputs
        self.engine_state["input_connections"] = [
            AudioConnection(ac).as_dict() for ac in s.engine_state.input_connections
        ]
        self.engine_state["output_connections"] = [
            AudioConnection(ac).as_dict() for ac in s.engine_state.output_connections
        ]

        self.tracks = [TrackInfo(t).as_dict() for t in s.tracks]

        self.state = {
            "sushi_info": self.sushi_info,
            "save_date": self.save_date,
            "midi_state": self.midi_state,
            "engine_state": self.engine_state,
            "tracks": self.tracks,
        }


def build_initial_state(config: dict, sc: SushiController) -> list:
    init_state = []
    for track in config['tracks']:
        for plugin in track['plugins']:
            p_state = {'processor': plugin['name'],
                       'parameters': {},
                       'properties': {}
                       }
            p_id = sc.audio_graph.get_processor_id(plugin['name'])

            # BYPASS 
            p_state['bypassed'] = sc.audio_graph.get_processor_bypass_state(p_id)
            
            # PROPERTIES
            for prop in sc.parameters.get_processor_properties(p_id):
                p_state['properties'][prop.name] = sc.parameters.get_property_value(p_id, prop.id)

            # PARAMETERS                
            ps = sc.audio_graph.get_processor_state(p_id)
            for p in ps.parameters:
                p_name = sc.parameters.get_parameter_info(p_id, p.parameter.parameter_id).name
                p_state['parameters'][p_name] = sc.parameters.get_parameter_value(p_id, p.parameter.parameter_id)
            init_state.append(p_state)

    return init_state


def build_config_dict(sc: SushiController) -> dict:
    s = sc.session.get_session()

    st = SessionState(s)

    config = {"host_config": {}, "tracks": []}
    config["host_config"]["samplerate"] = st.engine_state["sample_rate"]
    config["host_config"]["playing_mode"] = st.engine_state["playing_mode"]
    config["host_config"]["tempo_sync"] = st.engine_state["sync_mode"]
    config["host_config"]["tempo"] = st.engine_state["tempo"]

    for t in st.tracks:
        if t["type"] == "regular":
            track = {
                "name": t["name"],
                "label": t["label"],
                "channels": t["channels"],
                "inputs": [],
                "outputs": [],
                "plugins": [build_plugin_config(ps) for ps in t["processors"]],
            }
            config["tracks"].append(track)

    for ic in st.engine_state["input_connections"]:
        input_conn = {
            "engine_channel": ic["engine_channel"],
            "track_channel": ic["track_channel"],
        }
        if trk := next((t for t in config["tracks"] if t["name"] == ic["track"]), None):
            trk["inputs"].append(input_conn)

    for oc in st.engine_state["output_connections"]:
        output_conn = {
            "engine_channel": oc["engine_channel"],
            "track_channel": oc["track_channel"],
        }
        if trk := next((t for t in config["tracks"] if t["name"] == oc["track"]), None):
            trk["outputs"].append(output_conn)

    config['initial_state'] = build_initial_state(config, sc)
    return config


def build_plugin_config(plugin_state) -> dict:
    p_dict = {
        "name": plugin_state["name"],
        "label": plugin_state["label"],
        "type": plugin_state["type"],
    }
    match plugin_state["type"]:
        case "lv2":
            p_dict["uri"] = plugin_state["path"]
        case "internal":
            if "BW " in plugin_state["name"]:
                p_dict["uid"] = f"sushi.brickworks.{p_dict['name'][3:]}".lower()
            else:
                p_dict["uid"] = f"sushi.testing.{p_dict['name']}".lower()
        case "vst2x":
            p_dict["path"] = plugin_state["path"]
        case "vst3x":
            p_dict["path"] = plugin_state["path"]
            p_dict["uid"] = plugin_state["label"]

    return p_dict


def write_json_config_file(file_name: str, sc: SushiController) -> None:
    with open(file_name, "w") as f:
        f.write(json.dumps(build_config_dict(sc), indent=2))


if __name__ == "__main__":
    sc = SushiController()
    write_json_config_file(DEFAULT_DUMPED_CONFIG_FILENAME, sc)
