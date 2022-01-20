#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab
import nrzi
import zlib


def audio_open():
    pa = pyaudio.PyAudio()

    amplitude = 0.1
    framerate = 44000

    length = 0.25
    freq1  = 440
    freq2  = 880

    stream = pa.open(
            output=True,
            channels=1,
            rate=framerate,
            format=pa.get_format_from_width(2),
        )
    return stream

def encode(src, dst, msg):
    # Wywołamy funkcję:
    #encode(1,2,'abc')
    # żeby przesłać wiadomość abc od 1 do 2

    # Reprezentacja src,dst,msg na bitach
    # src, dst : int (rzutowanie na 6 bajtów)

    src = struct.pack('!LH', src//(2**16), src%(2**16))
    dst = struct.pack('!LH', dst//(2**16), dst%(2**16))
    #msg : bytes, str
    if isinstance(msg, str):
        msg = bytes(msg, 'utf8')

    #reprezentacja przez bitarray
    ln = struct.pack("!H", len(msg))

    bytes_ = src+dst+msg+ln
    crc = zlib.crc32(bytes_)
    crc = struct.pack('!L', crc)

    bytes_ = bytes_ + crc
    

    b = bitarray.bitarray()
    b.frombytes(bytes_)

    result = nrzi.nrzi_(bytes_)
    preamble = '10101010' * 7 + '10101011'
    preamble = bitarray.bitarray(preamble)

    result = preamble + result
    # Skonstruować ramkę
    # ramka = dst + src + struct.pack("!H", len(msg)) + msg
    # ramka = ramka + crc32(ramka)
    # crc32: potraktuj bity jako współczynniki, dopisz 32 zera na końcu. Podziel z resztą przez 100000100110000010001110110110111 i zwrócić resztę z dzielenia.

    # Skonstruować ciąg bitów do nadania
    # preamble = '10101010' * 7 + '10101011'
    # bity = preamble + nrzi(4b5b(ramka))

    # w NRZI pierwszy bit reprezentujemy jako zmianę względem ostatniej jedynki w preambule.

    #Wyemitować
    stream = audio_open()

    stream.write(result)
