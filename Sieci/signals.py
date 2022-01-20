import numpy
import pyaudio
import audio
import math

FRAMRATE = 44000


def sample_maker(frequency, time):
    sample_length = math.floor(FRAMRATE / frequency)
    sample_number = math.floor(FRAMRATE * time / sample_length)
    sample = [0]*sample_length
    for i in range(sample_length):
        sample[i] = numpy.sin(numpy.pi*2*i/sample_length)
    audio_bytes = audio.audio_to_byte(numpy.array(sample*sample_number))
    return audio_bytes


"""def sample_maker(sample_length, sample_number):
    sample = [0]*sample_length
    for i in range(sample_length):
        sample[i] = numpy.sin(numpy.pi*2*i/sample_length)
    audio_bytes = audio.audio_to_byte(numpy.array(sample*sample_number))
    return audio_bytes"""


audio_1 = sample_maker(880,0.25)
audio_0 = sample_maker(440,0.25)
"""audio_result = audio_0 + audio_1 + audio_0 + audio_1
audio_result = audio_result * 10
pa = pyaudio.PyAudio()
stream = audio.speaker_open(pa)
stream.write(audio_result)
stream.stop_stream()
stream.close()
pa.terminate()"""

