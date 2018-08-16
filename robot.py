import utilities
import time
import pygame
import os
import logging
import spectrum
import settings
import pyaudio
import sounddevice
from multiprocessing.pool import ThreadPool

# This is needed to fake out pygame.display.init()
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Start microphone data collection stream
sampler = spectrum.SWHear(updatesPerSecond=10, device=settings.CLEAN_MIC)
sampler.stream_start()
lastRead = sampler.chunksRead

audio = pyaudio.PyAudio()
vt3_stream = sounddevice.Stream(device=settings.SYNTH_MIC)

# Start another microphone for pass-thru

# Show progress of the program
logging.basicConfig(level=logging.DEBUG)

# initialize pygame
pygame.display.init()
pygame.mixer.init(frequency=44100, channels=2, size=-16)

# Start background music
sound_file = utilities.background_sound_player("background_sound/")

# Start without recording enabled
record_to_file = False
recording = []
recording_buffer = []
record_counter = 0

# Counters for determining beginning and end of speech
speaker_begin = 0
speaker_end = 0

# Define for the whole method
interrupt_thread = None
resume_thread = None
pool = ThreadPool(processes=1)

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
            interrupt_thread = pool.apply_async(
                utilities.interrupt_background_sound,
                args=(event.sound_file,)
            )
        elif event.type == 26:
            logging.info("Speaker is done. Play a fun sound then"
                         "resume background")
            position, interrupt_sound_file = interrupt_thread.get()
            utilities.resume_background_sound(position, interrupt_sound_file)

    # get the next new sample
    while lastRead == sampler.chunksRead:
        time.sleep(.1)
    lastRead = sampler.chunksRead

    """
    # If we are recording, get the data into a list for later file capture.
    if record_to_file:
        recording.append(sampler.stream.read(sampler.chunk))
        record_counter = record_counter + 1
    else:
        # Always keep the last several audio chunks to build a complete
        # recording
        while len(recording_buffer) >= settings.RECORDING_BUFFER_SIZE:
            recording_buffer.pop(0)
        recording_buffer.append(sampler.stream.read(sampler.chunk))
    """

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
