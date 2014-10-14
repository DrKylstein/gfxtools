#! /usr/bin/python3

import argparse
import sys
import io
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description='''Converts indexed image on stdin to packed pixel byte stream 
    at stdout.''')
    parser.add_argument('-b','--bpp', type=int, default=8, help='Number of bits per pixel.')
    parser.add_argument('-i', '--interleave', type=int, default=1, help=
        'Split image into row fields.')
    parser.add_argument('-c', '--columns', type=int, default=1, help=
        'Split image into column fields.')
    parser.add_argument('-p', '--padding', type=int, default=0, help=
        'Pad each row field with this many zeros.')
    args = parser.parse_args()
    
    #Image.open needs seek(), but stdin can't do that, so we dump all the bytes 
    #and re-create the stream from that
    image = Image.open(io.BytesIO(sys.stdin.buffer.read()))
    
    pixels_per_byte = 8 // args.bpp
        
    for j in range(args.interleave):
        for k in range(args.columns):
            for y in range(image.size[1]//args.interleave):
                for x in range(image.size[0] // args.columns // pixels_per_byte):
                    byte = 0
                    for i in range(pixels_per_byte):
                        byte <<= args.bpp
                        pixel = image.getpixel(((x*args.columns + k)*pixels_per_byte + i, y*args.interleave + j))
                        byte |= pixel
                    sys.stdout.buffer.write(bytes([byte]))
        for i in range(args.padding):
            sys.stdout.buffer.write(bytes([0]))