"""Generate sample datasets.

Filter by hash prefix."""
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

SET_SIZE = 1_500_000

HASH_WIDTH = 160
TARGET = '739437bb3dd6d1983e66629c5f08c70e52769371'  # bitcoin-puzzle-67
FILTER = '66'#TARGET[:2]

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
        hash_hex = key_2_hash(key)
        if hash_hex[:len(filter)] != filter:
            continue

        hash_bits = int_to_bin(int(hash_hex, 16), hash_width)

        source.append(hash_bits)
        result.append(int_to_bin(key, 1))
    print('FILTERED', len(result))
    return np.array(source, dtype=np.dtype('uint8')), np.array(result, dtype=np.dtype('uint8')), 

def to_str(a):
    return " ".join(str(round(i)) for i in a)

source, result = generate(SET_SIZE, HASH_WIDTH, FILTER)
data = np.hstack((source, result))

np.savetxt(f'prefix.k{KEY_WIDTH}.s{SEED}.{SET_SIZE // 1000}k.f{FILTER}.csv.gz', data, fmt="%d")
