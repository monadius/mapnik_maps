import os
import sys
import argparse
import plistlib
from PIL import Image, ImageDraw

# Command line arguments
    
parser = argparse.ArgumentParser(description="Creates a map of cities from a plist data file")

parser.add_argument('--png8', action='store_true',
                    help="8-bit PNG images")

parser.add_argument('-o', '--out', metavar='PATH',
                    help="the output file")

parser.add_argument('--color', default='red',
                    help="fill color for cities (use 'none' for no color)")

parser.add_argument('--marker-size', type=float, default=10.0,
                    help="marker size for cities")

parser.add_argument('--border', type=float, default=0.5,
                    help="marker border width for cities (0 = no border)")

parser.add_argument('--border-color', default='black',
                    help="marker border color for cities")

parser.add_argument('--input',
                    help="background file (should have the correct size)")

parser.add_argument('input_file',
                    help="input plist data file")

parser.add_argument('cities', nargs='*',
                    help="a list of cities (if empty then maps for all cities in the input data file are created)")

args = parser.parse_args()


data = plistlib.readPlist(args.input_file)

width = data['width']
height = data['height']
cities = data['cities']

canvas = None
rel_flag = False
if args.input:
    canvas = Image.open(args.input).convert('RGBA')
    if canvas.width != width or canvas.height != height:
        print("Using relative coordinates")
        width = canvas.width
        height = canvas.height
        rel_flag = True

if not canvas:
    canvas = Image.new('RGBA', (width, height), (255, 255, 255, 0))

d = ImageDraw.Draw(canvas)

for city in cities:
    name = city['name']
    if rel_flag:
        rx = city['rel_x']
        ry = city['rel_y']
        x = int(rx * width)
        y = int((1 - ry) * height)
    else:
        x = int(city['x'])
        y = int(city['y'])
    try:
        if x < 0 or x >= width or y < 0 or y >= height:
            print("Bad pixel value: ({0}, {1}) {2}".format(x, y, name))
        else:
            canvas.putpixel((x, y), (255, 0, 0, 255))
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=args.color)
    except:
        print("[ERROR]: ({0}, {1})".format(x, y))

if not args.out:
    args.out = args.input_file + ".png"

canvas.save(args.out)