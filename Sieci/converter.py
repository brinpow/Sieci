from bitarray import bitarray

CONVERT_DICT = {
    "0000": bitarray("11110"),
    "0001": bitarray("01001"),
    "0010": bitarray("10100"),
    "0011": bitarray("10101"),
    "0100": bitarray("01010"),
    "0101": bitarray("01011"),
    "0110": bitarray("01110"),
    "0111": bitarray("01111"),
    "1000": bitarray("10010"),
    "1001": bitarray("10011"),
    "1010": bitarray("10110"),
    "1011": bitarray("10111"),
    "1100": bitarray("11010"),
    "1101": bitarray("11011"),
    "1110": bitarray("11100"),
    "1111": bitarray("11101"),
}


def convert_4b5b(barray):
    if len(barray) % 4 != 0:
        raise Exception('Zła ilość bitów')
    result = bitarray(0)
    for i in range(int(len(barray)/4)):
        result = result + CONVERT_DICT[barray[4*i:4*i+4].to01()]
    return result


def convert_to_nrzi(barray):
    result = bitarray(len(barray)+1)
    result[0] = False
    for i in range(len(barray)):
        if barray[i]:
            if result[i]:
                result[i+1] = False
            else:
                result[i+1] = True
        else:
            result[i+1] = result[i]
    return result
