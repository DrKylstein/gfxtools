#! /usr/bin/python3
from PIL import Image
import argparse
import sys
import io

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts palette from an image at stdin to raw RGB888 on stdout.')
    parser.add_argument('-c', '--colors', default=256, type=int,  help='Number of colors to store in palette mode.')
    parser.add_argument('-s', '--shift', default=2, type=int, help='Bits to shift right, default is 2, for VGA.')
    args = parser.parse_args()
        
    file = sys.stdout.buffer

    #Image.open needs seek(), but stdin can't do that, so we dump all the bytes 
    #and re-create the stream from that
    image = Image.open(io.BytesIO(sys.stdin.buffer.read()))

    lut = image.palette.getdata()[1]
    for i in range(min(args.colors*3,len(lut))):
        octet = lut[i];
        file.write(bytes([octet>>args.shift]))
