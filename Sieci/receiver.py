import pyaudio

import decoder
import audio
import numpy
from bitarray import bitarray


def receive_wf(wave_file, baud_rate):
    step = int(audio.FRAMERATE/baud_rate)
    frames = audio.audio_read(wave_file, int(1000*audio.FRAMERATE))
    mess = bitarray()
    for i in range(0, len(frames), step):
        res = numpy.fft.rfft(frames[i:i+step])
        res = numpy.abs(res)
        max_index = numpy.where(res == numpy.amax(res))[0][0]
        frequency = max_index*baud_rate
        if numpy.abs(frequency-440) == 0:
            mess.append(False)
        elif numpy.abs(frequency-880) == 0:
            mess.append(True)

    #print(mess.to01())
    result = decoder.decode(mess)
    print(result)


def receive(mic, baud_rate):
    mess = []
    mess_prob = []
    bit_mess = bitarray()
    end = False
    start = False
    fsize = int(audio.FRAMERATE/baud_rate)
    while not end:
        frames = audio.audio_read(mic, fsize)
        res = numpy.fft.rfft(frames)
        res = numpy.abs(res)
        max_index = numpy.where(res == numpy.amax(res))[0][0]
        frequency = max_index*baud_rate
        #print(frequency)
        if numpy.abs(frequency-440) < 50:
            mess.append(frames)
            start = True
        elif numpy.abs(frequency-880) < 50:
            mess.append(frames)
            start = True
        else:
            if start:
                end = True
                mess.append(frames)

    for i in range(len(mess)):
        mess_prob.extend(mess[i])
    mess = mess_prob
    rv = probe(mess[4*fsize:8*fsize], fsize)
    k = int(fsize / 80)
    mess = mess[k*rv:]
    while len(mess) > fsize:
        cur_frame = mess[:fsize]
        res = numpy.fft.rfft(cur_frame)
        res = numpy.abs(res)
        max_index = numpy.where(res == numpy.amax(res))[0][0]
        frequency = max_index * baud_rate
        if numpy.abs(frequency - 440) < 50:
            bit_mess.append(False)
        elif numpy.abs(frequency - 880) < 50:
            bit_mess.append(True)
        mess = mess[fsize:]

    print(bit_mess.to01())
    print(rv)
    result = decoder.decode(bit_mess[4:])
    print(result)


def probe(arr, size):
    max_ = -1
    max_i = 0
    k = int(size / 80)
    for i in range(160):
        frames = arr[i*k:size+i*k]
        res = numpy.fft.rfft(frames)
        res = numpy.abs(res)
        cur_max = numpy.amax(res)
        #print(cur_max)
        if max_ == -1 or cur_max > max_:
            max_ = cur_max
            max_i = i
    return max_i


if __name__ == '__main__':
    i = input("Co słuchamy\n")
    tempo = int(input("Ile sygnałów na sek?\n"))
    if i == '0':
        pa = pyaudio.PyAudio()
        mic = audio.mic_open(pa)
        receive(mic, tempo)
        audio.audio_close(mic)
        pa.terminate()
    else:
        wf = audio.wave_open('code3.wav')
        receive_wf(wf, tempo)
        wf.close()
