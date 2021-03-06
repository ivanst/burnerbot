import settings
import pyaudio
import time

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(2),
                channels=1,
                rate=44100,
                input=True,
                output=True,
                input_device_index=settings.SYNTH_MIC,
                output_device_index=settings.SYNTH_OUT,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
