#! /usr/bin/python3
import argparse
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Takes a raw unsigned 8-bit pcm on stdin and outputs a delta-encoded bitstream on stdout.')
    
    input = sys.stdin.buffer
    output = sys.stdout.buffer
    
    pack = 0
    last = 0
    bitsRemaining = 8
    bs = input.read(1)
    while len(bs) > 0:
        sample = bs[0]
        pack >>= 1
        if sample > last:
            pack  |= 0x80
            last = min(last + 2, 255)
        else:
            last = max(last - 2, 0)
        bitsRemaining -= 1
        if bitsRemaining == 0:
            output.write(bytes([pack]))
            bitsRemaining = 8
        bs = input.read(1)