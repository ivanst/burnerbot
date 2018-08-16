import os
import settings
import logging
import random
import pygame
import time
import math
import struct
import numpy as np
import wave
import pyaudio


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
    pygame.mixer.music.play(loops=0, start=start / 1000)
    logging.info("Background sound player playing " + sound_file)
    return sound_file


def interrupt_background_sound(background_sound_file,
                               fade_time=settings.FADE_TIME):
    """
    Stop the pygame.music.play background sound and return stopping position
        and filename.
    Params:
        background_sound_file: The sound file that was being played
        interrupt_sound: The sound file to interrupt with
        fade_time: How long to fade
    """
    print(background_sound_file)
    position = pygame.mixer.music.get_pos() + fade_time
    logging.info("Stopping music position is " + str(position))
    pygame.mixer.music.set_endevent()
    pygame.mixer.music.fadeout(fade_time)
    logging.info("beginning " + str(fade_time) + " millisecond fade")
    time.sleep(fade_time / 1000)
    return position, background_sound_file


def play_foreground_sound(sound_file="interrupt_sound/phone.ogg"):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


def resume_background_sound(position, background_sound_file):
    # first make sure nothing is playing
    while pygame.mixer.music.get_busy():
        time.sleep(.25)
    background_sound_player(play_file=background_sound_file, start=position)


def get_rms(sound_block):
    """
    RMS amplitude is defined as the square root of the mean over time of the
    square of the amplitude. So we need to convert this string of bytes into
    a string of 16-bit samples...
    Params:
        sound_block: The sound block to sample from
    """

    count = len(sound_block) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, sound_block)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768.
        # normalize it to 1.0
        n = sample * 1.0 / 32768.0
        sum_squares += n * n

    return math.sqrt(sum_squares / count)


def frequency_volume_trigger(frequency_dictionary, frequency_ignore_dictionary,
                             sample):
    """
    If ALL frequencies in the dictionary exceed accompanying amplitude, returns
    true

    :param frequency_dictionary: A dictionary containing the frequency position
        and trigger amplitude at which to trigger. All must be exceeded to
        trigger.
    :param frequency_ignore_dictionary: A dictionary containing the frequency
        position and amplitudes at which we should ignore the sound. All must
        be observed as over limit to ignore.
    :param sample: Sound sample to evaluate
    """
    ignore_tests = 0
    for position, amplitude in frequency_ignore_dictionary.items():
        if sample[position] > amplitude:
            ignore_tests = ignore_tests + 1
    if ignore_tests == len(frequency_ignore_dictionary):
        logging.info("We just heard a bunch of noise. Ignoring...")
        return False

    for position, amplitude in frequency_dictionary.items():
        if sample[position] < amplitude:
            return False

    return True


def averaged_spectrogram(np_data_array, divisions=60):
    spectrogram_array = []
    num_chunk_elements = np_data_array.size // divisions
    i = 0
    while i < divisions:
        chunk_array = np_data_array[i*num_chunk_elements:(i+1)*num_chunk_elements]
        spectrogram_array.append(int(np.mean(chunk_array) / 1000))
        i = i+1
    return spectrogram_array


def save_audio_data(audio_data):
    logging.info("Saving audio to file")
    cursor = wave.open("sound.wav", "wb")
    cursor.setnchannels(2)
    cursor.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    cursor.setframerate(44100)
    cursor.writeframes(b''.join(audio_data))
    cursor.close()


def passthrough():
    WIDTH = 2
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        return in_data, pyaudio.paContinue

    stream = p.open(
                    format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    stream_callback=callback,
                    input_device_index=settings.SYNTH_MIC,
                    output_device_index=settings.MIXED_OUT,
                )

    stream.start_stream()

    global record
    while record:
        time.sleep(0.2)

    stream.stop_stream()
    stream.close()

    p.terminate()
