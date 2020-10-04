#! /usr/bin/python3
from PIL import Image
import argparse
import sys
import io

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Takes an image file on stdin and outputs a raw planar bitmap on stdout.')
    parser.add_argument('planes', type=int,
        help='Number of bit planes to output.')
    parser.add_argument('-i', '--interleave', type=int, default=0, help=
        'Switch planes after this many bytes. The default is contiguous planes.')
    parser.add_argument('-s', '--solid', action='store_true', help=
        'Produce a mask plane, but fill it with 1s')
    parser.add_argument('--ega', action='store_true', help=
        'Force default EGA palette')
        
    args = parser.parse_args()
        
    file = sys.stdout.buffer

    #Image.open needs seek(), but stdin can't do that, so we dump all the bytes 
    #and re-create the stream from that
    image = Image.open(io.BytesIO(sys.stdin.buffer.read()))

    if image.size[0] % 8:
        print('Image width must be divisible by 8!', file=sys.stderr)
        exit(1)
        
    plane_size = image.size[0] * image.size[1] // 8
        
    data = bytearray()
    
    masked = 'transparency' in image.info
    transparent_color = 0
    color_planes = args.planes
    colors = dict(zip(range(1 << args.planes),range(1 << args.planes)))
    if masked and not args.solid:
        color_planes -= 1
        try:
            transparent_color = image.info['transparency'][0]
        except TypeError:
            transparent_color = image.info['transparency']
        for key,item in colors.items():
            if item > transparent_color:
                colors[key] -= 1

    if masked:
        for y in range(image.size[1]):
            for b in range(image.size[0]//8):
                octet = 0;
                for x in range(8):
                    if args.solid or image.getpixel((b*8 + x,y)) != transparent_color:
                        octet = octet + (0x80 >> x)
                data.append(octet)
        
    for p in range(color_planes):
        for y in range(image.size[1]):
            for b in range(image.size[0]//8):
                octet = 0;
                for x in range(8):
                    if colors[image.getpixel((b*8 + x,y)) & (2**color_planes-1)] & (1 << p):
                        octet = octet + (0x80 >> x)
                data.append(octet)
                
    if args.interleave > 0:
        offsets = [i*plane_size for i in range(args.planes)]
        for contiguous_section in range(plane_size // args.interleave):
            for plane in range(args.planes):
                for current_byte in range(args.interleave):
                    file.write(data[offsets[plane]:offsets[plane]+1])
                    offsets[plane] += 1
    else:
        file.write(data)
            
