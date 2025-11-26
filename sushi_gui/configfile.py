from elkpy.sushicontroller import SushiController
from elkpy import sushi_info_types as st
import json


def build_config_dict(sc: SushiController) -> dict:
    """This will get all configuration info from Sushi and package it in a dictionary"""
    config = {"host_config": {}, "tracks": []}

    # Getting host config data
    sample_rate = int(sc.transport.get_samplerate())
    playing_mode = sc.transport.get_playing_mode().name.lower()
    sync_mode = sc.transport.get_sync_mode().name.lower()
    tempo = sc.transport.get_tempo()

    config["host_config"]["samplerate"] = sample_rate
    config["host_config"]["playing_mode"] = playing_mode
    config["host_config"]["tempo_sync"] = sync_mode
    config["host_config"]["tempo"] = tempo

    # Getting all tracks
    all_tracks = sc.audio_graph.get_all_tracks()
    for track in all_tracks:
        t = {
            "name": track.name,
            "channels": track.channels,
            "processors": get_processors_for_track(track.id, sc),
        }
        config["tracks"].append(t)

    return config


def get_processors_for_track(track_id: int, sc: SushiController) -> dict:
    processors = []

    all_processors = sc.audio_graph.get_track_processors(track_id)
    for processor in all_processors:
        proc = sc.audio_graph.get_processor_info(processor.id)
        p = {
            "name": proc.name,
            "uid": "fill in uid here",
            "path": "fill in path here",
            "type": "fill in type here",
        }
        processors.append(p)
    return processors


def write_json_config_file(file_name: str, config: dict) -> None:
    with open(file_name, "w") as f:
        f.write(json.dumps(config, indent=2))


if __name__ == "__main__":
    sc = SushiController()
    write_json_config_file("test_conf.json", build_config_dict(sc))
