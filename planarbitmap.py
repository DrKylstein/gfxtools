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
        
    for p in range(args.planes):
        for y in range(image.size[1]):
            for b in range(image.size[0]//8):
                octet = 0;
                for x in range(8):
                    if image.getpixel((b*8 + x,y)) & (1 << p):
                        octet = octet + (0x80 >> x);
                data.append(octet)#file.write(bytes([octet]))

    if args.interleave > 0:
        offsets = [i*plane_size for i in range(args.planes)]
        for contiguous_section in range(plane_size // args.interleave):
            for plane in range(args.planes):
                for current_byte in range(args.interleave):
                    file.write(data[offsets[plane]:offsets[plane]+1])
                    offsets[plane] += 1
    else:
        file.write(data)
            
