#! /usr/bin/python3

import argparse
import sys
import io
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
description='''Converts tileset image on stdin to linear strip of tiles at stdout. 
Image format is preserved, but color table may be padded.''')
    parser.add_argument('width', type=int, help='width of one tile')
    parser.add_argument('height', type=int, help='height of one tile')
    args = parser.parse_args()
    
    #Image.open needs seek(), but stdin can't do that, so we dump all the bytes 
    #and re-create the stream from that
    source = Image.open(io.BytesIO(sys.stdin.buffer.read()))
    
    tiles = (source.size[0]//args.width)*(source.size[1]//args.height)
    
    dest = source.resize((args.width, tiles*args.height))
    
    x = 0
    y = 0
    for i in range(tiles):
        dest.paste(source.crop((x, y, x+args.width, y+args.height)), (0,i*args.height))
        x += args.width
        if x >= source.size[0]:
            x = 0
            y += args.height;
    
    dest.save(sys.stdout.buffer, source.format)
    