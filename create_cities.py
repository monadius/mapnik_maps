import os
import sys
import argparse
import json
import plistlib

# Global variables

base_dir = '/Users/monad/Work/data'
cult10m_dir = os.path.join(base_dir, '10m_cultural', '10m_cultural')
phys10m_dir = os.path.join(base_dir, '10m_physical')
cult50m_dir = os.path.join(base_dir, '50m_cultural')
phys50m_dir = os.path.join(base_dir, '50m_physical')
edited50m_dir = os.path.join(base_dir, 'edited50m')

cities_file_50m = os.path.join(cult50m_dir, 'ne_50m_populated_places.shp')
land_file_50m = os.path.join(phys50m_dir, 'ne_50m_land.shp')
land_boundaries_file_50m = os.path.join(phys50m_dir, 'ne_50m_coastline.shp')
boundaries_file_50m = os.path.join(edited50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp')
countries_file_50m = os.path.join(cult50m_dir, 'ne_50m_admin_0_countries.shp')
lakes_file_50m = os.path.join(phys50m_dir, 'ne_50m_lakes.shp')

cities_file_10m = os.path.join(cult10m_dir, 'ne_10m_populated_places.shp')
land_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_sovereignty.shp')
land_boundaries_file_10m = os.path.join(phys10m_dir, 'ne_10m_land.shp')
boundaries_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_boundary_lines_land.shp')
countries_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_countries.shp')
lakes_file_10m = os.path.join(phys10m_dir, 'ne_10m_lakes.shp')

lakes_size = 3

def report_error(msg):
    sys.stderr.write("**ERROR**: {0}\n".format(msg))

# Command line arguments
    
parser = argparse.ArgumentParser(description="Creates a map of cities from a data file")

size_group = parser.add_mutually_exclusive_group()
size_group.add_argument('--size', nargs=2, metavar=('W', 'H'),
                        type=int, default=None,
                        help="the size of output images")
size_group.add_argument('--xd', action='store_true',
                        help="xd size (should be set in the input data file)")
size_group.add_argument('--hd', action='store_true',
                        help="0.5 * (xd size)")
size_group.add_argument('--hd2', action='store_true',
                        help="0.75 * (xd size)")
size_group.add_argument('--sd', action='store_true',
                        help="0.25 * (xd size)")

data_group = parser.add_mutually_exclusive_group()
data_group.add_argument('--50m', dest='use50m', action='store_true',
                        help="use 50m data")
data_group.add_argument('--10m', dest='use10m', action='store_true',
                        help="use 10m data (default)")

parser.add_argument('--capitals', action='store_true',
                    help="select capitals only")

parser.add_argument('--region-capitals', action='store_true',
                    help="select regional capitals only")

parser.add_argument('--png8', action='store_true',
                    help="8-bit PNG images")

parser.add_argument('--out', metavar='DIR',
                    help="the output directory")

parser.add_argument('--color', default='white',
                    help="fill color for cities (use 'none' for no color)")

parser.add_argument('--marker-size', type=float, default=8.0,
                    help="marker size for cities")

parser.add_argument('--border', type=float, default=1.8,
                    help="marker border width for cities (0 = no border)")

parser.add_argument('--border-color', default='black',
                    help="marker border color for cities")

parser.add_argument('--scale', type=float, default=1.0,
                    help="scale for lines and markers")

parser.add_argument('--land', action='store_true',
                    help="render the land layer")

parser.add_argument('--extra',
                    help="a file with additional cities which are not added to the output plist")

parser.add_argument('input_file',
                    help="input JSON data file")

parser.add_argument('cities', nargs='*',
                    help="a list of cities (if empty then maps for all cities in the input data file are created)")

# Parse arguments and load the input file

args = parser.parse_args()

with open(args.input_file) as f:
    data = json.load(f)

class CityInfo:
    def __init__(self, data):
        try:
            self.marker_size = None
            self.marker_offset = None
            self.out_name = None
            if isinstance(data, unicode):
                self.name = data.encode()
            elif isinstance(data, str):
                self.name = data
            else:
                assert(isinstance(data, dict))
                self.name = data['name'].encode()
                if 'out' in data:
                    self.out_name = data['out'].encode()
                if 'marker-size' in data:
                    self.marker_size = tuple(data['marker-size'])
                if 'marker-offset' in data:
                    self.marker_offset = tuple(data['marker-offset'])
        except UnicodeEncodeError as e:
            report_error("Bad character in: {0}".format([data]))
            raise e
        if not self.out_name:
            self.out_name = self.name

cities = []
cities_dict = {}
for city in data['cities']:
    info = CityInfo(city)
    cities.append(info)
    cities_dict[info.name] = info

extra_cities = []
if args.extra:
    with open(args.extra) as f:
        extra_data = json.load(f)
    for city in extra_data['cities']:
        extra_cities.append(CityInfo(city))

# Validate data

if 'xd-size' not in data:
    report_error("'xd-size' is not defined in {0}".format(args.input_file))
    exit(2)

if ('proj' not in data) or ('bbox' not in data):
    report_error("'proj' or 'bbox' are not defined in {0}".format(args.input_file))
    exit(2)

xd_width, xd_height = data['xd-size']

if args.use50m:
    cities_file = cities_file_50m
    land_file = land_file_50m
    land_boundaries_file = land_boundaries_file_50m
    boundaries_file = boundaries_file_50m
    countries_file = countries_file_50m
    lakes_file = lakes_file_50m
else:
    cities_file = cities_file_10m
    land_file = land_file_10m
    land_boundaries_file = land_boundaries_file_10m
    boundaries_file = boundaries_file_10m
    countries_file = countries_file_10m
    lakes_file = lakes_file_10m
    
# Validate arguments

if args.sd:
    width, height = int(xd_width * 0.25), int(xd_height * 0.25)
    args.scale *= 0.25
elif args.hd:
    width, height = int(xd_width * 0.5), int(xd_height * 0.5)
    args.scale *= 0.5
elif args.hd2:
    width, height = int(xd_width * 0.75), int(xd_height * 0.75)
    args.scale *= 0.75
elif args.xd:
    width, height = xd_width, xd_height
elif args.size:
    width, height = args.size
else:
    width, height = xd_width, xd_height

offset_scale_x = float(width) / xd_width
offset_scale_y = float(height) / xd_height

if args.color == 'none':
    args.color = None

if args.scale < 0.01 or args.scale > 10:
    sys.stderr.write("\nBad scale: {0}\n\n".format(args.scale))
    sys.exit(1)
    
if width < 1 or height < 1 or width > 10000 or height > 10000:
    sys.stderr.write("\nBad image size: {0} x {1}\n\n".format(width, height))
    sys.exit(1)

if not args.out:
    args.out = "out_{0}_{1}_{2}".format(data['name'], width, height)

if not os.path.exists(args.out):
    os.makedirs(args.out)

def escape(s):
    return s.replace("'", "\\'").replace('"', '\\"')

# Styles and layers

def add_layer_with_style(m, layer, style, style_name=None):
    if not style_name:
        style_name = layer.name + 'Style'
    m.append_style(style_name, style)
    layer.styles.append(style_name)
    m.layers.append(layer)

# Land

def land_style():
    s = Style()
    r = Rule()
    ps = PolygonSymbolizer()
    ps.fill = Color('#f1daa0')
    r.symbols.append(ps)
    s.rules.append(r)
    return s

def land_layer():
    ds = Shapefile(file=land_file)
    layer = Layer('Land')
    layer.datasource = ds
    return layer

# Land boundaries

def land_boundaries_style():
    s = Style()
    r = Rule()
    ls = LineSymbolizer()
    ls.stroke = Color('#4fadc2')
    ls.stroke_width = 1.0
    r.symbols.append(ls)
    s.rules.append(r)
    return s

def land_boundaries_layer():
    ds = Shapefile(file=land_boundaries_file)
    layer = Layer('Land Boundaries')
    layer.datasource = ds
    return layer

# Lakes

def lakes_style():
    s = Style()
    r = Rule()
    r.filter = Expression("[scalerank] <= {0}".format(lakes_size))
    ps = PolygonSymbolizer()
    ps.fill = Color('#b3e2ee')
    r.symbols.append(ps)
    ls = LineSymbolizer()
    ls.stroke = Color('#4fadc2')
    ls.stroke_width = 1.0
    r.symbols.append(ls)
    s.rules.append(r)
    return s

def lakes_layer():
    ds = Shapefile(file=lakes_file)
    layer = Layer('Lakes')
    layer.datasource = ds
    return layer

# Boundaries of countries

def boundaries_style():
    s = Style()
    r = Rule()
    ls = LineSymbolizer()
    ls.stroke = Color('#808080')
    ls.stroke_width = 1.5
    r.symbols.append(ls)
    s.rules.append(r)
    return s

def boundaries_layer():
    ds = Shapefile(file=boundaries_file)
    layer = Layer('Boundaries')
    layer.datasource = ds
    return layer

# Cities

def cities_style(names, size=(10,10), offset=None):
    s = Style()
    r = Rule()
    if isinstance(size, float) or isinstance(size, int):
        size = (size, size)

    name_filter = " or ".join(["[NAMEASCII] = '{0}'".format(escape(name)) for name in names])
    if args.capitals:
        name_filter = "([FEATURECLA] = 'Admin-0 capital' or [FEATURECLA] = 'Admin-0 capital alt') and ({0})".format(name_filter)
    if args.region_capitals:
        name_filter = "[FEATURECLA] = 'Admin-1 capital' and ({0})".format(name_filter)
    r.filter = Expression(name_filter)

    ms = MarkersSymbolizer()
    ms.allow_overlap = True
    # ms.max_error = 0

    if args.color:
        ms.fill = Color(args.color)
#        ms.opacity = 0.4

    if args.border > 0:
        ms.stroke = Color(args.border_color)
        ms.stroke_width = args.border
    else:
        ms.stroke_width = 0

    ms.width = Expression('{0}'.format(size[0] * args.scale))
    ms.height = Expression('{0}'.format(size[1] * args.scale))
    if offset:
        ms.transform = 'translate({0}, {1})'.format(offset[0] * offset_scale_x, offset[1] * offset_scale_y)

    r.symbols.append(ms)
    s.rules.append(r)
    return s

def cities_layer(names):
    ds = Shapefile(file=cities_file)
    layer = Layer("Cities " + ",".join(names))
    layer.datasource = ds
    return layer

# Features

def get_all_cities(names):
    ds = Shapefile(file=cities_file)
    result = {x['NAMEASCII'].encode(): x for x in ds.all_features() 
                if x['NAMEASCII'] in names
                if not args.capitals or x['FEATURECLA'].startswith('Admin-0 capital')
                if not args.region_capitals or x['FEATURECLA'] == 'Admin-1 capital'}
    diff = set(names) - set(result.keys())
    for name in diff:
        print("[WARNING]: bad name: {0}".format(name))
    return result

def get_projected_coordinates(m, feature):
    c = feature.geometry.centroid()
    p = Coord(c.x, c.y)
    proj = Projection(m.srs)
    return m.view_transform().forward(proj.forward(p))

# Base map

def base_map(data, width, height):
    m = Map(width, height, data['proj'].encode())

    if args.land:
        m.background = Color('#b3e2ee')
        add_layer_with_style(m, land_layer(),
                             land_style(), 'Land Style')
        add_layer_with_style(m, boundaries_layer(),
                             boundaries_style(), 'Boundaries Style')
        add_layer_with_style(m, land_boundaries_layer(),
                             land_boundaries_style(), 'Land Boundaries Style')
        add_layer_with_style(m, lakes_layer(),
                             lakes_style(), 'Lakes Style')

    m.zoom_to_box(Box2d(*data['bbox']))
    return m

# The main script

from mapnik import *

out_format = 'png256' if args.png8 else 'png'

m = base_map(data, width, height)

city_names = [city.name for city in cities] + [city.name for city in extra_cities]
add_layer_with_style(m, cities_layer(city_names), 
                     cities_style(city_names, size=args.marker_size), 'All Cities')

render_to_file(m, os.path.join(args.out, 'a.png'), out_format, args.scale)

def check_name(name):
    if not args.cities:
        return True
    for x in args.cities:
        if name.startswith(x):
            return True
    return False

names = []
for city in cities:
    name = city.name
    if not check_name(name):
        continue
    names.append(name)

features = get_all_cities(names)
coords = []

for name, f in features.iteritems():
    c = get_projected_coordinates(m, f)
    coords.append({
        'name': cities_dict[name].out_name,
        'x': c.x,
        'y': c.y,
        'rel_x': c.x / float(width),
        'rel_y': 1 - c.y / float(height)
    })

result = {
    'width': width,
    'height': height,
    'cities': coords
}

plistlib.writePlist(result, os.path.join(args.out, 'a.plist'))

print("done")
