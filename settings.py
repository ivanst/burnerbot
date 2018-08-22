# Devices
CLEAN_MIC = 7
SYNTH_MIC = 6
SYNTH_OUT = 6

# How long to fade music
FADE_TIME = 1000
# Background volume level
BG_VOLUME = 1.0
BG_VOLUME_MINIMUM = .2
SYNTH_VOLUME = 100
SYNTH_VOLUME_MINIMUM = 30

RECORDING_BUFFER_SIZE = 30
RECORD_MAX_VOLUME = 500
RECORD_MAX_SAMPLE_LENGTH = 2

# Speaker detection
SPEAKER_BEGIN_CYCLES = 2
SPEAKER_END_CYCLES = 6
SPEAKER_MAX_CYCLES = 1000000

# Spectrum position and level trigger key
SPECTRUM_TRIGGER_LEVELS = {
    1: 1000,
    2: 1000
}

# Spectrum that we want to ignore by. Anything detected in these levels will
# cause us to act as if nobody is talking. It should just be bad noise caught
# here
SPECTRUM_IGNORE_LEVELS = {
    15: 9000,
    16: 9000,
}
