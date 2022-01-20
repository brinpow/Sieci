#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab
 
import numpy
import pyaudio
import wave
import sys
 
CHUNK = 1024
CHANNELS = 1
SAMPLE_WIDTH = 2
SAMPLE_TYPE = numpy.dtype('<i2')
SAMPLE_MAX = 2**15 - 1
FRAMERATE = 44000

numpy.set_printoptions(threshold=sys.maxsize)


def wave_open(path):
    audio = wave.open(path, 'rb')
    return audio


def wave_open_write(path):
    audio = wave.open(path, 'wb')
    return audio


def mic_open(pa):
    audio = pa.open(
        input=True,
        channels=CHANNELS,
        rate=FRAMERATE,
        format=pa.get_format_from_width(SAMPLE_WIDTH),
    )
    return audio


def speaker_open(pa):
    audio = pa.open(
        output=True,
        channels=CHANNELS,
        rate=FRAMERATE,
        format=pa.get_format_from_width(SAMPLE_WIDTH),
    )
    return audio


def audio_read(audio, chunk=CHUNK):
    if isinstance(audio, wave.Wave_read):
        raw = audio.readframes(chunk)
    else:
        raw = audio.read(chunk)
    frames = numpy.frombuffer(raw, dtype=SAMPLE_TYPE).astype(float)
    frames /= SAMPLE_MAX
    frames.clip(-1, 1)
    return frames


def audio_to_byte(frames):
    audio_bytes = (frames*SAMPLE_MAX).astype(SAMPLE_TYPE).tobytes()
    return audio_bytes


def audio_close(audio):
    if isinstance(audio, wave.Wave_read):
        audio.close()
    else:
        audio.stop_stream()
        audio.close()


def sample_maker(sample_length, sample_number):
    sample = [0]*sample_length
    for i in range(sample_length):
        sample[i] = numpy.sin(numpy.pi*2*i/sample_length)
    audio_bytes = audio_to_byte(numpy.array(sample*sample_number))
    return audio_bytes


def frames_maker(sample_length, sample_number):
    sample = [0]*sample_length
    for i in range(sample_length):
        sample[i] = numpy.sin(numpy.pi*2*i/sample_length)
    return numpy.array(sample*sample_number)


def frames_to_wave(path, frames):
    wave_file = wave_open_write(path)
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(SAMPLE_WIDTH)
    wave_file.setframerate(FRAMERATE)
    wave_file.writeframes(audio_to_byte(frames))
    wave_file.close()


def set_wave_file(wave_file):
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(SAMPLE_WIDTH)
    wave_file.setframerate(FRAMERATE)

def to_speaker(frames):
    pa = pyaudio.PyAudio()
    stream = speaker_open(pa)
    stream.write(audio_to_byte(frames))
    stream.stop_stream()
    stream.close()
    pa.terminate()


def audio_write(audio, frames):
    #audio_bytes = (frames*SAMPLE_MAX).astype(SAMPLE_TYPE).tobytes()
    if isinstance(audio, wave.Wave_write):
        audio.writeframes(frames)
    else:
        audio.write(frames)


"""audio = None
if len(sys.argv) > 1:
    audio = wave_open(sys.argv[1])
else:
    audio = mic_open(pa)

print(audio_read(audio))

audio_close(audio)"""
