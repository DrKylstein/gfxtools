#! /usr/bin/python3
from PIL import Image
import argparse
import sys
import io

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Replaces a range of colors in an indexed image.')
    parser.add_argument('match', type=int, help='start of color range to replace')
    parser.add_argument('replace', type=int, help='color to replace start with')
    parser.add_argument('count', type=int, help='number of colors past start to replace')
    parser.add_argument('-x','--exchange', action='store_true', help='exchange the two color ranges')
    args = parser.parse_args()
        
    #Image.open needs seek(), but stdin can't do that, so we dump all the bytes 
    #and re-create the stream from that
    image = Image.open(io.BytesIO(sys.stdin.buffer.read()))
    pixels = image.load()

    for y in range(image.size[1]):
        for x in range(image.size[0]):
            if pixels[x,y] >= args.match and pixels[x,y]-args.match < args.count:
                pixels[x,y] = args.replace + pixels[x,y]-args.match
            if not args.exchange:
                continue
            if pixels[x,y] >= args.replace and pixels[x,y]-args.replace < args.count:
                pixels[x,y] = args.match + pixels[x,y]-args.replace
                

    image.save(sys.stdout.buffer, "png")
