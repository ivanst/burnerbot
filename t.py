import utilities
import time
import pygame
import os
import logging
import spectrum

# This is needed to fake out pygame.display.init()
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Start microphone data collection stream
sampler = spectrum.SWHear(updatesPerSecond=10)
sampler.stream_start()
lastRead = sampler.chunksRead

# Show progress of the program
logging.basicConfig(level=logging.DEBUG)

# initialize pygame
pygame.display.init()
pygame.mixer.init(frequency=44100, channels=2, size=-16)

# Start background music
global sound_file
sound_file = utilities.background_sound_player("background_sound/")

while True:
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
            logging.info("Interrupt signal received")
            utilities.interrupt_sound_player(event.sound_file)

    while lastRead == sampler.chunksRead:
        time.sleep(.1)
    lastRead = sampler.chunksRead
    if sampler.fft[0] > 10000:
        print("FFT signal[0] is " + str(sampler.fft[0]))
        pygame.event.post(pygame.event.Event(25, sound_file=sound_file))
