import os
import pydub

SOURCE_FOLDER = "/Users/ivan/Desktop/sounds/Background Tracks/"
#SOURCE_FOLDER = "/Users/ivan/Desktop/sounds/Final Responses One/"
DESTINATION_FOLDER = "/Users/ivan/Desktop/oggs/Background Tracks/"
#DESTINATION_FOLDER = "/Users/ivan/Desktop/oggs/Final Responses One/"

files = os.listdir(SOURCE_FOLDER)

for file in files:
    if file == ".DS_Store":
        continue
    newfile = file[:-3] + "ogg"
    sound = pydub.AudioSegment.from_wav(SOURCE_FOLDER + file)
    sound.export(DESTINATION_FOLDER + newfile, format="ogg", codec="vorbis",
                 bitrate="320k", parameters=["-strict", "-2"])
