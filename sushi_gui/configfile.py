from elkpy.sushicontroller import SushiController
from elkpy import sushi_info_types as st


def build_config_json(sc: SushiController) -> dict:
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
            "processors": get_processors_for_track(track.id),
        }
        config["tracks"].append(t)

    return config


def get_processors_for_track(track_id: int, sc: SushiController) -> dict:
    processors = []

    all_processors = sc.audio_graph.get_track_processors(track_id)
    for processor in all_processors:
        sc.audio_graph.get_processor_info()


if __name__ == "__main__":
    sc = SushiController()
    print(build_config_json(sc))
