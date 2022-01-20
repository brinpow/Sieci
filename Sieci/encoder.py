import nrzi
import zlib
import audio
import pyaudio
import struct
from bitarray import bitarray
import signals


def speaker(code):
    pa = pyaudio.PyAudio()
    stream = audio.speaker_open(pa)
    audio_0 = signals.sample_maker(440, 0.1)
    audio_1 = signals.sample_maker(880, 0.1)
    for i in range(len(code)):
        if code[i]:
            stream.write(audio_1)
        else:
            stream.write(audio_0)
    pa.terminate()


def encode(src, dst, msg):
    src = struct.pack('!LH', src//(2**16), src % (2**16))
    dst = struct.pack('!LH', dst//(2**16), dst % (2**16))

    if isinstance(msg, str):
        msg = bytes(msg, 'utf8')

    ln = struct.pack("!H", len(msg))
    bytes_ = src+dst+ln+msg
    crc = zlib.crc32(bytes_)
    crc = struct.pack('!L', crc)
    bytes_ = bytes_ + crc

    result = nrzi.nrzi_(nrzi.k4b5b(bytes_))
    preamble = '10101010' * 7 + '10101011'
    preamble = bitarray(preamble)
    result = preamble + result
    return result


#encode(1, 2, 'abc')
