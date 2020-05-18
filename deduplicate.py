#! /usr/bin/python3

import argparse
import sys
import io
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
description='''Converts tileset image on stdin to linear strip of tiles at stdout. 
Image format is preserved, but color table may be padded.''')
    parser.add_argument('--height', type=int, default=0, help='height of one tile, defaults to image width')
    parser.add_argument('-n','--names', type=argparse.FileType('w'), help='a list of tile indexes for recreating the original sequence will be written to this file')
    args = parser.parse_args()
    
    #Image.open needs seek(), but stdin can't do that, so we dump all the bytes 
    #and re-create the stream from that
    source = Image.open(io.BytesIO(sys.stdin.buffer.read()))
    
    if args.height == 0:
        args.height = source.size[0]
    
    tiles = []
    names = []
    
    for i in range(int(source.size[1] / args.height)):
        sample = source.crop((0, i * args.height, source.size[0], (i+1) * args.height))
        match = False
        for tile, j in zip(tiles, range(len(tiles))):
            if sample.tobytes() == tile.tobytes():
                names.append(j)
                match = True
                break
        if match:
            continue
        tiles.append(sample)
        names.append(len(tiles)-1)
        
    dest = source.resize((source.size[0], len(tiles)*args.height))

    for tile, i in zip(tiles, range(len(tiles))):
        dest.paste(tile, (0,i*args.height))
        
    dest.save(sys.stdout.buffer, source.format)
    
    if args.names is not None:
        if len(tiles) > 256:
            args.names.write(' '.join(map('{0:#06x}'.format, names)))
        else:
            args.names.write(' '.join(map('{0:#04x}'.format, names)))
        
    print('{} unique tiles'.format(len(tiles)), file=sys.stderr)