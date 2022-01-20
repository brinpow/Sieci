#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab

from bitarray import bitarray
CONVERT_DICT = {
    "0000": "11110",
    "0001": "01001",
    "0010": "10100",
    "0011": "10101",
    "0100": "01010",
    "0101": "01011",
    "0110": "01110",
    "0111": "01111",
    "1000": "10010",
    "1001": "10011",
    "1010": "10110",
    "1011": "10111",
    "1100": "11010",
    "1101": "11011",
    "1110": "11100",
    "1111": "11101",
}


def k4b5b(ramka):
    b = bitarray()
    b.frombytes(ramka)
    c = bitarray()
    for i in range(0, len(b), 4):
        c.extend(CONVERT_DICT[b[i:i+4].to01()])
    return c


def nrzi_(bity):
    p = True
    c = bitarray()
    for i in range(len(bity)):
        if bity[i]:
            p = not p
        c.append(p)
    return c


def dec_nrzi(bits):
    last = True
    result = bitarray()
    for i in range(len(bits)):
        if last == bits[i]:
            result.append(False)
        else:
            result.append(True)
        last = bits[i]
    return result


def dec_4b5b(bits):
    result = bitarray()
    for i in range(0, len(bits), 5):
        for c4b, c5b in CONVERT_DICT.items():
            if c5b == bits[i:i + 5].to01():
                result.extend(c4b)
                break
    return result.tobytes()
