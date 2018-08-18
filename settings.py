# Devices
CLEAN_MIC = 7
SYNTH_MIC = 6
MIXED_OUT = 7

# How long to fade music
FADE_TIME = 1000
# Background volume level
BG_VOLUME = 1.0
SYNTH_VOLUME = 100
# Wait this long after levels drop below "speaking" levels
END_SPEAKING_TIME = 1

RECORDING_BUFFER_SIZE = 30
RECORD_MAX_VOLUME = 500
RECORD_MAX_SAMPLE_LENGTH = 2

# Speaker detection
SPEAKER_BEGIN_CYCLES = 5
SPEAKER_END_CYCLES = 5
SPEAKER_MAX_CYCLES = 1000000

# Spectrum position and level trigger key
SPECTRUM_TRIGGER_LEVELS = {
    2: 20,
    3: 20,
}

# Spectrum that we want to ignore by. Anything detected in these levels will
# cause us to act as if nobody is talking. It should just be bad noise caught
# here
SPECTRUM_IGNORE_LEVELS = {
    15: 60,
    16: 60,
}
