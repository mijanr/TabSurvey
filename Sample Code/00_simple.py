"""Generate sample datasets.

Filter by number of bits in result hash."""
import random
import numpy as np

from bitcoinlib.keys import Key
from bitcoinlib.encoding import pubkeyhash_to_addr

def int_to_bin(i, width):
    return [(i >> j) & 1 for j in range(width)]

def hex_to_bin(i, width):
    return int_to_bin(int(i, 16), width)

SEED = 112 #221
random.seed(SEED)

SET_SIZE = 100_000

HASH_WIDTH = 160
TARGET = '739437bb3dd6d1983e66629c5f08c70e52769371'  # bitcoin-puzzle-67
FILTER = sum(hex_to_bin(TARGET, HASH_WIDTH))

KEY_MIN_WIDTH = 66
KEY_WIDTH = 67

def key_2_hash(key):
    key_hex = hex(key)[2:].rjust(64, '0')
    return Key(key_hex).hash160.hex()

def generate(count, hash_width, filter):
    source, result = [], []
    for i in range(count):
        if i % 10000 == 0:
            print(i)
        key = random.randrange(2 ** KEY_MIN_WIDTH, 2 ** KEY_WIDTH)
        hash = key_2_hash(key)

        hash_bits = int_to_bin(hash, hash_width)
        if sum(hash_bits) != filter:
            continue

        source.append(hash_bits)
        result.append(int_to_bin(key, 1))
    print('FILTERED', len(result))
    return np.array(source, dtype=np.dtype('uint8')), np.array(result, dtype=np.dtype('uint8')), 

def to_str(a):
    return " ".join(str(round(i)) for i in a)

source, result = generate(SET_SIZE, HASH_WIDTH, FILTER)
data = np.hstack((source, result))

np.savetxt(f'simple.k{KEY_WIDTH}.s{SEED}.{SET_SIZE // 1000}k.f{FILTER}.csv.gz', data, fmt="%d")
