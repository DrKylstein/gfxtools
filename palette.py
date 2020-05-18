#! /usr/bin/python3
from PIL import Image
import argparse
import sys
import io

def bit_sequence_to_int(l):
    return sum(j<<i for i,j in enumerate(reversed(l)))

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts palette from an image at stdin to raw binary on stdout.')
    parser.add_argument('-c', '--colors', default=256, type=int,  help='Number of colors to store.')
    parser.add_argument('-f', '--format', default='00rrrrrr00gggggg00bbbbbb', help='Bit format, defaults to 00rrrrrr00gggggg00bbbbbb for VGA')
    args = parser.parse_args()
        
    file = sys.stdout.buffer

    #Image.open needs seek(), but stdin can't do that, so we dump all the bytes 
    #and re-create the stream from that
    image = Image.open(io.BytesIO(sys.stdin.buffer.read()))

    lut = image.palette.getdata()[1]
    for index in range(min(args.colors,len(lut)//3)):
        color = (lut[index*3],lut[index*3 + 1],lut[index*3 + 2])
        colorBit = [0x80,0x80,0x80]
        colorChar = {'r':0,'g':1,'b':2}
        bits = []
        for c in args.format:
            if c is '0':
                bits.append(0)
            elif c is '1':
                bits.append(1)
            else:
                i = colorChar[c]
                bits.append(1 if (color[i] & colorBit[i]) else 0)
                colorBit[i] >>= 1
        file.write(bytes(map(bit_sequence_to_int, chunker(bits,8))))