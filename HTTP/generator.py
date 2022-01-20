#!/usr/bin/env python3

import hashlib

def last_zeros(hasher):
    d = hasher.digest()
    c = 0
    while len(d) > 0:
        b = int(d[-1])
        if b == 0:
            c += 8
            d = d[:-1]
        else:
            while b%2 == 0:
                c += 1
                b //= 2
            break
    return c

def generate(seed, chunk_bits, response_bits):
    hasher = hashlib.sha256()
    hasher.update(bytes(seed, 'utf-8'))
    chunk = ''
    while True:
        chunk += hasher.hexdigest()
        if last_zeros(hasher) >= response_bits:
            yield chunk
            return
        if last_zeros(hasher) >= chunk_bits:
            yield chunk
            chunk = ''
        hasher.update(hasher.digest())

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default='start')
    parser.add_argument('--chunk-bits', type=int, default=8)
    parser.add_argument('--response-bits', type=int, default=16)
    args = parser.parse_args()
    for part in generate(seed=args.seed, chunk_bits=args.chunk_bits, response_bits=args.response_bits):
        print(part)