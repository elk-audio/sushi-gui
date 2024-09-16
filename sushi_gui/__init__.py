
INSTALLED_PLUGINS = {
    "plugins": {

        "Passthrough": {
            "name": "Passthrough",
            "uid": "sushi.testing.passthrough",
            "parameters": [],
            "description": "Simply a bypass."
        },

        "Gain": {
            "name": "Gain",
            "uid": "sushi.testing.gain",
            "parameters": [
                {
                    "name": "gain",
                    "unit": "dB",
                    "default": 0.83,
                    "normalized": {
                        "from": [-120, 24],
                        "default": 0.0
                    },
                    "description": "Gain in dB"
                }
            ],
            "description": "Simple gain plugin. Note that the input controls are not smoothed, so it is not suitable to be used in a real-time context where the gain is adjusted by the user. For those use cases, prefer using the internal gain parameter of the tracks."
        },

        "Equalizer": {
            "name": "Equalizer",
            "uid": "sushi.testing.equalizer",
            "parameters": [
                {
                    "name": "frequency",
                    "unit": "Hz",
                    "default": 0.05,
                    "normalized": {
                        "from": [20, 20000],
                        "default": 1000.0
                    },
                    "description": "Center frequency in Hertz"
                },
                {
                    "name": "gain",
                    "unit": "dB",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Output gain in dB"
                },
                {
                    "name": "q",
                    "unit": None,
                    "default": 0.1,
                    "normalized": {
                        "from": [0, 10],
                        "default": 1.0
                    },
                    "description": "Q factor of the filter"
                }
            ],
            "description": "Parametric peak equalizer (single band). The implementation is based on the warped bilinear transform following RBJ Audio Cookbook’s formulas. Parameters are smoothed and can be modulated at run-time."
        },

        "MonoSumming": {
            "name": "MonoSumming",
            "uid": "sushi.testing.mono_summing",
            "parameters": [],
            "description": "Simple plugin that sums all input channels to mono, and outputs the same mono audio to all channels."
        },

        "SamplePlayer": {
            "name": "SamplePlayer",
            "uid": "sushi.testing.sampleplayer",
            "parameters": [
                {
                    "name": "volume",
                    "unit": "dB",
                    "default": 0.77,
                    "normalized": {
                        "from": [-120, 36],
                        "default": 0.0
                    },
                    "description": "Static gain for the sample"
                },
                {
                    "name": "attack",
                    "unit": "s",
                    "default": 0.0,
                    "normalized": {
                        "from": [0, 10],
                        "default": 0.0
                    },
                    "description": "Envelope attack time in seconds"
                },
                {
                    "name": "decay",
                    "unit": "s",
                    "default": 0.0,
                    "normalized": {
                        "from": [0, 10],
                        "default": 0.0
                    },
                    "description": "Envelope decay time in seconds"
                },
                {
                    "name": "sustain",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Envelope sustain level"
                },
                {
                    "name": "release",
                    "unit": "s",
                    "default": 0.0,
                    "normalized": {
                        "from": [0, 10],
                        "default": 0.0
                    },
                    "description": "Envelope release time in seconds"
                }
            ],
            "properties": {
                "sample_file": "Path to .wav file to load"
            },
            "description": "Simple polyphonic sample-based player. Only one sample can be loaded and played with pitch tracking and ADSR envelope."
        },

        "Arpeggiator": {
            "name": "Arpeggiator",
            "uid": "sushi.testing.arpeggiator",
            "parameters": [
                {
                    "name": "range",
                    "unit": "oct",
                    "default": 0.25,
                    "normalized": {
                        "from": [1, 5],
                        "default": 2
                    },
                    "description": "Octave range, as integer"
                }
            ],
            "description": "Simple Arpeggiator that repeats in “UP” movement the held MIDI notes on the track, using Sushi’s tempo configuration."
        },

        "Transposer": {
            "name": "Transposer",
            "uid": "sushi.testing.transposer",
            "parameters": [
                {
                    "name": "transpose",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Center frequency in Hertz"
                }
            ],
            "description": "Transposes incoming MIDI Note On/Off events by a fixed amount of semitones."
        },

        "StepSequencer": {
            "name": "StepSequencer",
            "uid": "sushi.testing.equalizer",
            "parameters": [
                {
                    "name": "pitch_1",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_1",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_1",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                },
                {
                    "name": "pitch_2",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_2",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_2",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                },
                {
                    "name": "pitch_3",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_3",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_3",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                },{
                    "name": "pitch_4",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_4",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_4",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                },{
                    "name": "pitch_5",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_5",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_5",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                },
                {
                    "name": "pitch_6",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_6",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_6",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                },
                {
                    "name": "pitch_7",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_7",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_7",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                },{
                    "name": "pitch_8",
                    "unit": "semitone",
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Pitch in semitones"
                },
                {
                    "name": "step_8",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Step On/Off"
                },
                {
                    "name": "step_ind_8",
                    "unit": None,
                    "default": 1.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Indicator (output only) of this step's On/Off status"
                }
            ],
            "description": "A simple 8-step MIDI sequencer."
        },
        
        "PeakMeter": {
            "name": "PeakMeter",
            "uid": "sushi.testing.peakmeter",
            "parameters": [
                {
                    "name": "left",
                    "unit": "dB",
                    "default": None,
                    "normalized": {
                        "from": [-120, 0],
                        "default": None
                    },
                    "description": "(Output only) Detected level on the Left track in dB"
                },
                {
                    "name": "right",
                    "unit": "dB",
                    "default": None,
                    "normalized": {
                        "from": [-120, 0],
                        "default": None
                    },
                    "description": "(Output only) Detected level on the Right track in dB"
                }
            ],
            "description": "Basic plugin that analyzes the level of the incoming audio signal at 25 Hz rate and outputs parameter values corresponding to the detected level."
        },

        "CVtoControl": {
            "name": "CV to Control",
            "uid": "sushi.testing.cv_to_control",
            "parameters": [
                {
                    "name": "channel",
                    "unit": None,
                    "default": 0.0,
                    "normalized": {
                        "from": [0, 16],
                        "default": 0.0
                    },
                    "description": "MIDI channel"
                },
                {
                    "name": "tune",
                    "unit": None,
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Coarse tune parameter"
                },
                {
                    "name": "polyphony",
                    "unit": None,
                    "default": 0.0,
                    "normalized": {
                        "from": [1, 4],
                        "default": 1
                    },
                    "description": "Number of CV voices"
                },
                {
                    "name": "pitch_1",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 1"
                },
                {
                    "name": "velocity_1",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice1"
                },
                {
                    "name": "pitch_2",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 2"
                },
                {
                    "name": "velocity_2",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice 2"
                },
                {
                    "name": "pitch_3",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 3"
                },
                {
                    "name": "velocity_3",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice 3"
                },
                {
                    "name": "pitch_4",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 4"
                },
                {
                    "name": "velocity_4",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice 4"
                }
            ],
            "description": "Adapter plugin which converts CV/gate information to note on and note off messages, thus enabling CV/gate control of synthesizer plugins."
        },

        "ControlToCV": {
            "name": "Control to CV",
            "uid": "sushi.testing.control_to_cv",
            "parameters": [
                {
                    "name": "send_velocity",
                    "unit": None,
                    "default": False,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Switch velocity transmission on/off"
                },
                {
                    "name": "send_modulation",
                    "unit": None,
                    "default": False,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Switch modulation transmission on/off"
                },
                {
                    "name": "retrigger_enabled",
                    "unit": None,
                    "default": False,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Switch retrigger mode on/off"
                },
                {
                    "name": "tune",
                    "unit": None,
                    "default": 0.0,
                    "normalized": {
                        "from": [-24, 24],
                        "default": 0.0
                    },
                    "description": "Coarse tune parameter"
                },
                {
                    "name": "fine_tune",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [-1, 1],
                        "default": 0.0
                    },
                    "description": "Fine tune parameter"
                },
                {
                    "name": "polyphony",
                    "unit": None,
                    "default": 0.0,
                    "normalized": {
                        "from": [1, 4],
                        "default": 1
                    },
                    "description": "Number of CV voices"
                },
                {
                    "name": "modulation",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [-1, 1],
                        "default": 0.0
                    },
                    "description": "Modulation parameter"
                },
                {
                    "name": "pitch_1",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 1"
                },
                {
                    "name": "velocity_1",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice1"
                },
                {
                    "name": "pitch_2",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 2"
                },
                {
                    "name": "velocity_2",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice 2"
                },
                {
                    "name": "pitch_3",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 3"
                },
                {
                    "name": "velocity_3",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice 3"
                },
                {
                    "name": "pitch_4",
                    "unit": "semitones",
                    "default": 0.0,
                    "normalized": {
                        "from": None,
                        "default": None
                    },
                    "description": "Pitch for CV voice 4"
                },
                {
                    "name": "velocity_4",
                    "unit": None,
                    "default": 0.5,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.5
                    },
                    "description": "NoteON velocity for CV voice 4"
                }
            ],
            "description": "Adapter plugin to convert from NoteON/NoteOFF messages to CV/gate information, enabling CV/gate control from MIDI plugins."
        },

        "WavWriter": {
            "name": "Wav Writer",
            "uid": "sushi.testing.wav_writer",
            "parameters": [
                {
                    "name": "recording",
                    "unit": None,
                    "default": 0.0,
                    "normalized": {
                        "from": [0, 1],
                        "default": 0.0
                    },
                    "description": "Switch recording On/Off. Default: 0 for Off"
                },
                {
                    "name": "write_speed",
                    "unit": "s",
                    "default": 1.0,
                    "normalized": {
                        "from": [0.5, 4.0],
                        "default": 1.0
                    },
                    "description": "How often to write the audio data in seconds"
                }
            ],
            "properties": {
                "destination_file": "Path to and name of the file to write to. \".wav\" is appended to the file name automatically."
            },
            "description": "Passthrough plugin that writes the audio to a wav file."
        }
    }
}


