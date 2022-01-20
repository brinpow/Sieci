import zlib

import nrzi
import struct


def decode(bits):
    last = bits[0]
    for i in range(1, len(bits)):
        if bits[i] == last and bits[i]:
            bits = bits[i+1:]
            break
        elif bits[i] == last and not(bits[i]):
            raise Exception("Error, wrong preamble")
        else:
            last = bits[i]
    frame = nrzi.dec_4b5b(nrzi.dec_nrzi(bits))
    src = frame[:6]
    src = struct.unpack('!LH', src)[1]
    dst = frame[6:12]
    dst = struct.unpack('!LH', dst)[1]
    ln = frame[12:14]
    ln = struct.unpack("!H", ln)[0]
    core = frame[:-4]
    frame = frame[14:]
    crc = frame[ln:]
    msg = frame[:ln]
    msg = msg.decode("utf8")
    try:
        crc = struct.unpack('!L', crc)[0]
        if crc == zlib.crc32(core):
            print("OK")
        else:
            print("crc")
    except Exception:
        print("crc")
    #else:
        #raise Exception("Wrong crc32 code")
    #print(src, dst, msg)
    return src, dst, msg


"""decode(bitarray("10101010101010101010101010101010101010101010101010101010101010110101101011010110101101011"
                "010110101101011010110101101011100010101101011010110101101011010110101101011010110101101011001110"
                "10110101101011001100101110001101001100001011001101001110101100101100011000110101011110101"))"""
