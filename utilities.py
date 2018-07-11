import os
import settings
import logging
import random
import pygame
import time
import audioop
import math
import struct
import numpy


def select_random_file_from_directory(path, last_file=None):
    """
    selects a random file from path. If last_file is provided, it will not be
    returned. This prevents repeats.
    Args:
        path (str): the path to the directory where the files to be randomly
            selected are kept
        last_file (str): the last file selected. Provide this to avoid selecting
            the same file twice.

    Returns:
        random file name selected form directory with full path.

    """
    files = os.listdir(path)
    randomized_files_list = random.sample(files, 2)
    if path + randomized_files_list[0] != last_file:
        return_file = randomized_files_list[0]
    else:
        return_file = randomized_files_list[1]
    logging.info("Selected file is " + return_file)
    return path + return_file


def background_sound_player(sound_files_path=None, start=0, play_file=None,
                            last_file=None):
    """
    A sound player that randomly selects a sound file from sound_files_path and
    plays it.
    Args:
        sound_files_path (str): the path to all the background sound files
        start (float): Start position for music
        play_file (str): If provided, use this sound file instead of a random one
    Returns:
        Complete path to sound file used
    """
    if play_file is None:
        sound_file = select_random_file_from_directory(sound_files_path,
                                                       last_file)
    else:
        sound_file = play_file
    pygame.mixer.music.set_volume(settings.BG_VOLUME)
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.set_endevent(24)
    pygame.mixer.music.play(loops=0, start=start/1000)
    return sound_file


def interrupt_sound_player(background_sound_file, interrupt_sound="test",
                           fade_time=settings.FADE_TIME):
    """
    Stop the pygame.music. Play background_sound_file. Restart music where we
    left off.
    Params:
        background_sound_file: The sound file that was being played
        interrupt_sound: The sound file to interrupt with
        fade_time: How long to fade
    """
    position = pygame.mixer.music.get_pos() + 3000
    logging.info("Stopping music position is " + str(position))
    pygame.mixer.music.set_endevent()
    pygame.mixer.music.fadeout(fade_time)
    logging.info("beginning " + str(fade_time) + " millisecond fade")
    time.sleep(fade_time/1000)
    pygame.mixer.music.load("interrupt_sound/phone.ogg")
    pygame.mixer.music.play()
    time.sleep(5)
    background_sound_player(play_file=background_sound_file, start=position)


def get_rms(sound_block):
    """
    RMS amplitude is defined as the square root of the mean over time of the
    square of the amplitude. So we need to convert this string of bytes into
    a string of 16-bit samples...
    Params:
        sound_block: The sound block to sample from
    """

    count = len(sound_block)/2
    format = "%dh"%(count)
    shorts = struct.unpack(format, sound_block)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
    # sample is a signed short in +/- 32768.
    # normalize it to 1.0
        n = sample * 1.0/32768.0
        sum_squares += n*n

    return math.sqrt( sum_squares / count )


def volume_trigger(sound, length, max_volume):
    """
    If a volume is exceeded this function evaluates true and can activate other functions
    """
    volume = audioop.max(sound, length)
    if volume > max_volume:
        pygame.mixer.music.set_endevent(pygame.constants.USEREVENT + 1)
