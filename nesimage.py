#! /usr/bin/python3

import sys
import argparse
import itertools
from PIL import Image

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('input')
    argparser.add_argument('palette',type=argparse.FileType('wb'))
    argparser.add_argument('pattern',type=argparse.FileType('wb'))
    argparser.add_argument('name',type=argparse.FileType('wb'))
    argparser.add_argument('attribute',type=argparse.FileType('wb'))
    argparser.add_argument('-O','--optimize',action='store_true')
    args = argparser.parse_args()

    image = Image.open(args.input)
    
    palette = set()
    tiles = set()
    
    attribute_colors = []
    
    
    for ay in range(15):
        attribute_colors.append([])
        for ax in range(16):
            colors = set()
            for ny in [ay*2+i for i in range(2)]:
                for nx in [ax*2+i for i in range(2)]:
                    for py in [ny*8+i for i in range(8)]:
                        for px in [nx*8+i for i in range(8)]:
                            pixel = image.getpixel((px,py))
                            colors.add(pixel)
            if len(colors) > 4:
                print('Too many colors in attribute {},{}'.format(ax,ay))
                exit(1)
            palette.add(frozenset(colors))
            attribute_colors[ay].append(frozenset(colors))
    
    final_palette = set()
    for line in palette:
        small = False
        for other_line in palette:
            if other_line > line:
                small = True
                break
        if not small:
            final_palette.add(line)
    palette = final_palette
    
    if len(palette) > 4:
        print('Too many colors in image, {} sets'.format(len(final_palette)))
        for line in palette:
            print(','.join(map(hex,sorted(list(line)))))
        exit(1)
        
    bgs = set()
    for line in palette:
        for color in line:
            valid = True
            for other_line in palette:
                if color not in other_line and len(other_line) >= 4:
                    valid = False
                    break
            if valid:
                bgs.add(color)
    
    if len(bgs) < 1:
        print('No shared background color!')
        exit(1)
    
    raw_palette = []
    
    bg = sorted(list(bgs))[0]
    
    for line in palette:
        raw = [bg]
        for color in sorted(list(line)):
            if color not in raw:
                raw.append(color)
        raw_palette.append(raw)
        
    lines_p = tuple([tuple(map(lambda i: (bg,*i),itertools.permutations(tuple(line[1:])))) for line in raw_palette])
    palette_options = tuple(itertools.product(*lines_p))
    pattern_options = []
    tile_maps = []
    attribute_tables = []
    
    i = 0
    for palette_option in palette_options:
        patterns = set()
        tile_map = [[None for j in range(32)] for i in range(30)]
        attribute_table = []

        for ay in range(15):
            attribute_row = []
            for ax in range(16):
                colors = None
                for line in palette_option:
                    if set(line) >= attribute_colors[ay][ax]:
                        colors = line
                        break
                attribute_row.append(palette_option.index(colors))
                for ny in [ay*2+i for i in range(2)]:
                    for nx in [ax*2+i for i in range(2)]:
                        tile = []
                        for py in [ny*8+i for i in range(8)]:
                            row = []
                            for px in [nx*8+i for i in range(8)]:
                                pixel = image.getpixel((px,py))
                                row.append(colors.index(pixel))
                            tile.append(tuple(row))
                        patterns.add(tuple(tile))
                        tile_map[ny][nx] = tuple(tile)
            attribute_table.append(attribute_row)
        print('{} of {}: maybe {} tiles...'.format(i,len(palette_options),len(patterns)).ljust(40), end='\r')
        i += 1
        pattern_options.append(patterns)
        tile_maps.append(tile_map)
        attribute_tables.append(attribute_table)
        if not args.optimize and len(patterns) <= 256:
            break
        
    best_index = pattern_options.index(sorted(pattern_options,key=len)[0])
    print()
    print('{} tiles'.format(len(pattern_options[best_index])))
    for l in range(3,-1,-1):
        print(l)
        if l < len(palette_options[best_index]):
            line = palette_options[best_index][l]
            if len(line) < 4:
                line += tuple([bg for i in range(4-len(line))])
            args.palette.write(bytes(line[::-1]))
        else:
            args.palette.write(bytes([bg for i in range(4)]))
            
    pattern_table = tuple(pattern_options[best_index])
    for row in tile_maps[best_index]:
        for tile in row:
            args.name.write(bytes([pattern_table.index(tile)]))
    for tile in pattern_table:
        for plane in range(2):
            for row in tile:
                bits = 0
                for pixel in row:
                    bits <<= 1
                    if pixel & (plane+1):
                        bits |= 1
                args.pattern.write(bytes([bits]))
    print(len(tile_maps[best_index]),len(tile_maps[best_index][0]))
    for ay in range(8):
        for ax in range(8):
            bits = attribute_tables[best_index][ay*2][ax*2]
            bits |= attribute_tables[best_index][ay*2][ax*2+1] << 2
            if ay < 7:
                bits |= attribute_tables[best_index][ay*2+1][ax*2] << 4
                bits |= attribute_tables[best_index][ay*2+1][ax*2+1] << 6
            args.attribute.write(bytes([bits]))
            
                    
                    
    