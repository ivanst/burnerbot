import utilities
import time
import pygame
import os
import logging
import spectrum
import settings
import pyaudio
from multiprocessing.pool import ThreadPool

# This is needed to fake out pygame.display.init()
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Start microphone data collection stream
sampler = spectrum.SWHear(updatesPerSecond=10, device=settings.CLEAN_MIC)
sampler.stream_start()
lastRead = sampler.chunksRead

# Show progress of the program
logging.basicConfig(level=logging.DEBUG)

# initialize pygame
pygame.display.init()
pygame.mixer.init(frequency=44100, channels=2, size=-16)

# Start background music
sound_file = utilities.background_sound_player()

# Start without recording enabled
record_to_file = False
recording = []
recording_buffer = []
record_counter = 0
record = False

# Counters for determining beginning and end of speech
speaker_begin = 0
speaker_end = 0

# Define for the whole method
interrupt_thread = None
resume_thread = None
pool = ThreadPool(processes=3)

while True:
    # Process all events on the queue first
    for event in pygame.event.get():
        """
        Event Types:
        24 = background_song over
        25 = Interrupt signal received
        """
        time.sleep(1)
        if event.type == 24:
            logging.info("Background sound ended")
            sound_file = utilities.background_sound_player(
                "background_sound/",
                last_file=sound_file
            )
        elif event.type == 25:
            logging.info("Interrupt signal received.")
            utilities.synth_sound()
        elif event.type == 26:
            logging.info("Speaker is done. Play a fun sound then"
                         "resume background")
            utilities.synth_sound(False)
            pool.apply_async(utilities.foreground_sound())

    # get the next new sample
    while lastRead == sampler.chunksRead:
        time.sleep(.1)
    lastRead = sampler.chunksRead

    # get FFT data on latest sample
    sample = utilities.averaged_spectrogram(sampler.fft)
    #print(sample)
    # If audio spectrum levels get high enough long enough, we have a speaker.
    if utilities.frequency_volume_trigger(settings.SPECTRUM_TRIGGER_LEVELS,
                                          settings.SPECTRUM_IGNORE_LEVELS,
                                          sample):
        speaker_end = 0
        speaker_begin = speaker_begin + 1
        if speaker_begin >= settings.SPEAKER_BEGIN_CYCLES \
                and not record_to_file:
            # A speaker has spoken long enough to trigger recording and other
            # actions
            speaker_begin = 0
            record_to_file = True
            pygame.event.post(pygame.event.Event(25, sound_file=sound_file))
    else:
        # We had a cycle with inadequate levels or someone is currently
        # speaking. Restart the begin counter
        speaker_begin = 0
        # Someone is speaking. Cut them off after too long.
        if record_to_file:
            speaker_end = speaker_end + 1
            # We haven't had a voice trigger for a while or they were talking
            # too long. Take their recording.
            if speaker_end >= settings.SPEAKER_END_CYCLES or \
                    record_counter >= settings.SPEAKER_MAX_CYCLES:
                # Speaker is done. Cleanup and save their recording
                pygame.event.post(pygame.event.Event(26))
                record_counter = 0
                speaker_end = 0
                record_to_file = False
                recording = recording_buffer + recording
                recording_buffer = []
                #utilities.save_audio_data(recording)
                recording = []
