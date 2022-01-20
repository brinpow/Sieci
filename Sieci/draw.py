#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab

import matplotlib.pyplot as plt 
import numpy
import pyaudio
import wave
import sys
import time
import struct
 
CHUNK = 1024
CHANNELS = 1
SAMPLE_WIDTH = 2
SAMPLE_TYPE = numpy.dtype('<i2')
SAMPLE_MAX = 2**15 - 1
FRAMERATE = 44000

ANALYZE_LENGTH = 0.1
ANALYZE_TOTAL_LENGTH = 30

numpy.set_printoptions(threshold=sys.maxsize)

pa = pyaudio.PyAudio()


def wave_open(path):
    audio = wave.open(path, 'rb')
    return audio


def mic_open():
    audio = pa.open(
        input=True,
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


def audio_close(audio):
    if isinstance(audio, wave.Wave_read):
        audio.close()
    else:
        audio.stop_stream()
        audio.close()


audio = mic_open()

plt.ion()
fig = plt.figure()

for i in range(int(ANALYZE_TOTAL_LENGTH/ANALYZE_LENGTH)):
    res = audio_read(audio, int(ANALYZE_LENGTH * FRAMERATE))
    fre = numpy.fft.rfft(res)
    fre = numpy.abs(fre)
    if i*ANALYZE_LENGTH >= 1 and int(i*ANALYZE_LENGTH) != int((i-1)*ANALYZE_LENGTH):
        fig.clear()
        a = fig.add_subplot(311)
        b = fig.add_subplot(312)
        c = fig.add_subplot(313)
        a.plot(range(len(res)), res)
        b.plot(range(len(fre)), fre)
        c.plot(range(len(fre[0:1000])), fre[0:1000])
        fig.canvas.draw()
    print(numpy.argmax(fre)/ANALYZE_LENGTH)

plt.ioff()
plt.show()

audio_close(audio)
pa.terminate()
