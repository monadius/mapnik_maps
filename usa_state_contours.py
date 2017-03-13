import os
import sys
import argparse

# Global variables

xd_width, xd_height = 1200, 900

base_dir = '/Users/monad/Work/data'
#cult50m_dir = os.path.join(base_dir, '50m_cultural')
#data_file = os.path.join(cult50m_dir, 'ne_50m_admin_1_states_provinces_shp.shp')
data_file = os.path.join(base_dir, 'statesp010g.shp_nt00938', 'statesp010g.shp')

def report_error(msg):
    sys.stderr.write("**ERROR**: {0}\n".format(msg))

parser = argparse.ArgumentParser(description="Creates images of contours of all 50 states")

size_group = parser.add_mutually_exclusive_group()
size_group.add_argument('--size', nargs=2, metavar=('W', 'H'),
                        type=int, default=(xd_width, xd_height),
                        help="the size of output images")
size_group.add_argument('--xd', action='store_true',
                        help="equivalent to --size {0} {1}".format(xd_width, xd_height))
size_group.add_argument('--hd', action='store_true',
                        help="0.5 * (xd size)")
size_group.add_argument('--sd', action='store_true',
                        help="0.25 * (xd size)")

parser.add_argument('--png8', action='store_true',
                    help="8-bit PNG images")

parser.add_argument('--out', metavar='DIR',
                    help="the output directory")

parser.add_argument('--color', default='green',
                    help="polygon fill color (use 'none' for no color)")

parser.add_argument('--line-color', default='black',
                    help="border line color (use 'none' for no borders)")

parser.add_argument('--scale', type=float, default=1.0,
                    help="scale for lines")

parser.add_argument('states', nargs='*',
                    help="create images for given states only")


# Parse and validate arguments

args = parser.parse_args()

if args.sd:
    width, height = int(xd_width * 0.25), int(xd_height * 0.25)
    args.scale *= 0.25
elif args.hd:
    width, height = int(xd_width * 0.5), int(xd_height * 0.5)
    args.scale *= 0.5
elif args.xd:
    width, height = xd_width, xd_height
elif args.size:
    width, height = args.size
else:
    width, height = xd_width, xd_height

if args.color == 'none':
    args.color = None

if args.line_color == 'none':
    args.line_color = None
    
if args.scale < 0.01 or args.scale > 10:
    sys.stderr.write("\nBad scale: {0}\n\n".format(args.scale))
    sys.exit(1)
    
if width < 1 or height < 1 or width > 10000 or height > 10000:
    sys.stderr.write("\nBad image size: {0} x {1}\n\n".format(width, height))
    sys.exit(1)
    
if not args.out:
    args.out = "out_states_{0}_{1}".format(width, height)

if not os.path.exists(args.out):
    os.makedirs(args.out)

# Load geo data from a file

class GeoData:
    def __init__(self, name, proj4, coordinates):
        self.name = name
        self.proj4 = proj4
        self.coordinates = coordinates

    def __str__(self):
        return "{0}, proj = {1}, coords = {2}".format(self.name, self.proj4, self.coordinates)

def load_geo_data(fname):
    result = {}
    print("Loading: {0}".format(fname))
    with open(fname, 'r') as f:
        lines = [line.strip() for line in f]
    NAME=1
    PROJ=2
    COORD=3
    state = NAME
    for line in lines:
        if len(line) == 0:
            continue
        if state == NAME:
            if len(line) != 2:
                report_error("Bad line (a state abbreviation is expected): {0}".format(line))
                continue
            name = line.lower()
            if name in result:
                report_error("Repeated name: {0}".format(line))
            state = PROJ
        elif state == PROJ:
            proj = line
            state = COORD
        elif state == COORD:
            coords = tuple([float(x) for x in line.split(',')])
            if len(coords) != 4:
                report_error("Bad coordinates: {0}".format(line))
            result[name] = GeoData(name, proj, coords)
            state = NAME
    if state != NAME:
        report_error("Incomplete data for: {0}".format(name))
    return result
        

# Create maps

from mapnik import *

def state_style(state_abbrev):
    s = Style()
    r = Rule()

#    r.filter = Expression("[iso_3166_2] = 'US-{0}'".format(state_abbrev))
    r.filter = Expression("[STATE_ABBR] = '{0}' and [TYPE] = 'Land'".format(state_abbrev.upper()))

    if args.color:
        ps = PolygonSymbolizer()
        ps.fill = Color(args.color)
        r.symbols.append(ps)

    if args.line_color:
        ls = LineSymbolizer(Color(args.line_color), 1.0)
        r.symbols.append(ls)

    s.rules.append(r)
    return s


def state_layer(state_abbrev):
    ds = Shapefile(file=data_file)
    layer = Layer(state_abbrev)
    layer.datasource = ds
    return layer


def create_map(state, width, height):
    m = Map(width, height, state.proj4)

    style_name = 'State Style ' + state.name
    m.append_style(style_name, state_style(state.name))

    layer = state_layer(state.name)
    layer.styles.append(style_name)
    m.layers.append(layer)

    m.zoom_to_box(Box2d(*state.coordinates))
    return m
                   

# The main script

data = load_geo_data("50StatesGeoData.txt")

if not args.states:
    args.states = data.keys()

for name in args.states:
    name = name.lower()
    print("Processing: {0}".format(name))
    if name not in data:
        report_error("Bad state abbreviation: {0}".format(name))
        continue
    m = create_map(data[name], width, height)

    out_name = os.path.join(args.out, "{0}.png".format(name))
    out_format = 'png256' if args.png8 else 'png'

    render_to_file(m, out_name, out_format, args.scale)
    
print("done")
print("Run 'mogrify -trim +repage *.png' to trim images")
