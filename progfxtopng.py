#! /usr/bin/python3
from PIL import Image
import argparse
import sys
import io

def deinterleave(input):
    output = [0 for i in range(8)]
    for j in range(len(input)):
        for i in range(8):
            output[i] |= ((input[j] >> (7-i))&1) << j
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Converts a ProGraphx Toolbox Tileset to a PNG image.')
    parser.add_argument('--solid', '-s', action='store_true', 
        help='ignore mask plane', dest='notrans')
    args = parser.parse_args()

    file = sys.stdin.buffer

    count = file.read(1)[0]
    width = file.read(1)[0]
    height = file.read(1)[0]

    image = Image.new("P", (width*8, height*count))
    image.putpalette((
        0x00,0x00,0x00,
        0x00,0x00,0xAA, 
        0x00,0xAA,0x00,
        0x00,0xAA,0xAA,
        0xAA,0x00,0x00,
        0xAA,0x00,0xAA,
        0xAA,0x55,0x00,
        0xAA,0xAA,0xAA,
        0x55,0x55,0x55,
        0x55,0x55,0xFF,
        0x55,0xFF,0x55,
        0x55,0xFF,0xFF,
        0xFF,0x55,0x55,
        0xFF,0x55,0xFF,
        0xFF,0xFF,0x55,
        0xFF,0xFF,0xFF,
        0x00,0xFF,0x00
    ))
    
    for y in range(height*count):
        for x in range(width):
            mask = deinterleave(file.read(1))
            px = deinterleave(file.read(4))
            for j in range(8):
                point = (x*8 + j, y)
                if mask[j] or args.notrans:
                    image.putpixel(point, px[j])
                else:
                    image.putpixel(point, 16)

    image.save(sys.stdout.buffer, "png", transparency=16)
