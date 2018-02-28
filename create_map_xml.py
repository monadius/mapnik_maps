from __future__ import print_function
import os
import sys
import argparse
import json
from mapnik_xml import *

# Global variables

this_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
base_dir = '/Users/monad/Work/data'

marker_file = os.path.join(this_dir, "marker.svg")

cult10m_dir = os.path.join(base_dir, '10m_cultural', '10m_cultural')
phys10m_dir = os.path.join(base_dir, '10m_physical')
cult50m_dir = os.path.join(base_dir, '50m_cultural')
phys50m_dir = os.path.join(base_dir, '50m_physical')
edited50m_dir = os.path.join(base_dir, 'edited50m')

land_file_50m = os.path.join(cult50m_dir, 'ne_50m_admin_0_countries.shp')
land_boundaries_file_50m = os.path.join(phys50m_dir, 'ne_50m_coastline.shp')
boundaries_file_50m = os.path.join(edited50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp')
countries_file_50m = os.path.join(cult50m_dir, 'ne_50m_admin_0_countries.shp')
lakes_file_50m = os.path.join(phys50m_dir, 'ne_50m_lakes.shp')

land_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_sovereignty.shp')
land_boundaries_file_10m = os.path.join(phys10m_dir, 'ne_10m_land.shp')
boundaries_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_boundary_lines_land.shp')
countries_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_countries.shp')
lakes_file_10m = os.path.join(phys10m_dir, 'ne_10m_lakes.shp')

disputed_file = os.path.join(edited50m_dir, 'ne_50m_admin_0_disputed_areas.shp')

def report_error(msg):
    print("**ERROR**: {0}\n".format(msg), file=sys.stderr)

# Command line arguments
    
parser = argparse.ArgumentParser(description="Creates a map from a data file")

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

parser.add_argument('--png8', action='store_true',
                    help="8-bit PNG images")

parser.add_argument('--out', metavar='DIR',
                    help="the output directory")

parser.add_argument('--color', default='red',
                    help="polygon fill color for countries (use 'none' for no color)")

#parser.add_argument('--line-color', default='black',
#                    help="border line color (use 'none' for no borders)")

parser.add_argument('--lakes-size', type=int, default=3,
                    help="scale rank of rendered lakes (set a negative value for no lakes)")

parser.add_argument('--scale', type=float, default=1.0,
                    help="scale for lines")

parser.add_argument('--no-markers', action='store_true',
                    help="do not draw markers")

parser.add_argument('--top', action='store_true',
                    help="move the country layer above the land boundary layer")

parser.add_argument('--dependent', action='store_false', default=True,
                    help="color countries with their dependent territories")

parser.add_argument('--land-only', action='store_true',
                    help="render the land layer only")

parser.add_argument('--country-only', action='store_true',
                    help="render the country only")

parser.add_argument('--country-border-color', default='black',
                    help="the color of country borders (works only with --country-only)")

parser.add_argument('--test', action='store_true',
                    help="produce one map only")

parser.add_argument('--debug', action='store_true',
                    help="debug mode")

parser.add_argument('input_file',
                    help="input JSON data file")

parser.add_argument('countries', nargs='*',
                    help="a list of countries (if empty then maps for all countries in the input data file are created)")

# Parse arguments and load the input file

args = parser.parse_args()

with open(args.input_file) as f:
    data = json.load(f)

class CountryInfo:
    def __init__(self, data):
        self.disputed = None
        self.extra_disputed = None
        self.disputed_boundary = None
        self.one_color = False
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
            if 'disputed' in data:
                disputed = data['disputed']
                if isinstance(disputed, unicode) or isinstance(disputed, str):
                    disputed = [disputed]
                self.disputed = [s.encode() for s in disputed]
            if 'extra-disputed' in data:
                self.extra_disputed = data['extra-disputed'].encode()
            if 'one-color' in data:
                self.one_color = data['one-color']
            if 'disputed-boundary' in data:
                self.disputed_boundary = data['disputed-boundary']
            if 'marker-size' in data:
                self.marker_size = tuple(data['marker-size'])
            if 'marker-offset' in data:
                self.marker_offset = tuple(data['marker-offset'])
        if not self.out_name:
            self.out_name = self.name

countries = []
for country in data['countries']:
    countries.append(CountryInfo(country))
                
# Validate data

if 'xd-size' not in data:
    report_error("'xd-size' is not defined in {0}".format(args.input_file))
    exit(2)

if ('proj' not in data) or ('bbox' not in data):
    report_error("'proj' or 'bbox' are not defined in {0}".format(args.input_file))
    exit(2)

xd_width, xd_height = data['xd-size']

if args.use50m:
    land_file = land_file_50m
    land_boundaries_file = land_boundaries_file_50m
    boundaries_file = boundaries_file_50m
    countries_file = countries_file_50m
    lakes_file = lakes_file_50m
else:
    land_file = land_file_10m
    land_boundaries_file = land_boundaries_file_10m
    boundaries_file = boundaries_file_10m
    countries_file = countries_file_10m
    lakes_file = lakes_file_10m

if args.dependent:
    country_filter_template = "[name] = '{0}' or [admin] = '{0}' or [sovereignt] = '{0}'"
else:
    country_filter_template = "[name] = '{0}' or [admin] = '{0}'"
    
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

if args.country_border_color == 'none':
    args.country_border_color = None

#if args.line_color == 'none':
#    args.line_color = None
    
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

# Styles and layers

def add_layer_with_style(m, layer, style, style_name=None):
    if not style_name:
        style_name = layer.name + 'Style'
    m.append_style(style_name, style)
    layer.styles.append(style_name)
    m.layers.append(layer)

# Land

def land_layer():
    s = Style("Land")
    s.symbols.append(PolygonSymbolizer("#f1daa0"))
    return Layer("Land", land_file, s)

# Land boundaries

def land_boundaries_layer():
    s = Style("Land Boundaries")
    s.symbols.append(LineSymbolizer("#4fadc2", 1.0))
    return Layer("Land Boundaries", land_boundaries_file, s)

# Lakes

def lakes_layer():
    s = Style("Lakes")
    s.filter = "[scalerank] <= {}".format(args.lakes_size)
    s.symbols.append(PolygonSymbolizer("#b3e2ee"))
    s.symbols.append(LineSymbolizer("#4fadc2", 1.0))
    return Layer("Lakes", lakes_file, s)

# Boundaries of countries

def boundaries_layer():
    s = Style("Boundaries")
    s.symbols.append(LineSymbolizer("#808080", 1.5))
    return Layer("Boundaries", boundaries_file, s)

# Countries

def country_layer(name, boundary_flag=False):
    s = Style("Country " + name)
    s.filter = country_filter_template.format(name)
    if args.color:
        s.symbols.append(PolygonSymbolizer(args.color))
    if boundary_flag and args.country_border_color:
        s.symbols.append(LineSymbolizer(args.country_border_color, 1.5))
    return Layer("Country " + name, countries_file, s)

def disputed_layer(names, one_color=False, boundary=False, data_file=disputed_file):
    name = "Disputed " + ",".join(names)
    s = Style(name)
    s.filter = " or ".join("[name] = '{0}'".format(name) for name in names)
    ps = PolygonSymbolizer("#f76d50")
    if one_color and args.color:
        ps.fill = args.color
    s.symbols.append(ps)
    if boundary:
        s.symbols.append(LineSymbolizer(ps.fill, 1.5))
    return Layer(name, data_file, s)

def marker_layer(name, size=(10,10), offset=None):
    s = Style("Marker " + name)
    s.filter = country_filter_template.format(name)
    ms = MarkersSymbolizer(marker_file)
    ms.opacity = 0.4
    ms.scale = (size[0] * args.scale / 100.0, size[1] * args.scale / 100.0)
    if offset:
         ms.translation = (offset[0] * offset_scale_x, offset[1] * offset_scale_y)
    s.symbols.append(ms)
    return Layer("Marker " + name, countries_file, s)

# Base map

def create_base_map(data, width, height):
    m = Map(width, height, data["proj"].encode(), data["bbox"])
    if args.land_only:
        m.layers.append(land_layer())
    elif args.country_only:
        pass
    else:
        m.background = "#b3e2ee"
        m.layers.append(land_layer())
        m.layers.append(boundaries_layer())
        m.layers.append(land_boundaries_layer())
        m.layers.append(lakes_layer())
    return m

# A map with a country

def add_country_layers(m, info):
    layer = country_layer(info.name, boundary_flag=args.country_only)
    m.layers.append(layer)
    if info.disputed:
        layer = disputed_layer(info.disputed, one_color=info.one_color, boundary=info.disputed_boundary)
        m.layers.append(layer)
    if info.extra_disputed:
        layer = disputed_layer(info.extra_disputed, one_color=info.one_color, boundary=info.disputed_boundary, data_file=countries_file)
        m.layers.append(layer)
    if info.marker_size and not args.no_markers:
        layer = marker_layer(info.name, size=info.marker_size, offset=info.marker_offset)
        m.layers.append(layer)

def create_map(data, width, height, info):
    m = Map(width, height, data["proj"].encode(), data["bbox"])
    if args.land_only:
        m.layers.append(land_layer())
        add_country_layers(m, info)
    elif args.country_only:
        add_country_layers(m, info)
    else:
        m.background = "#b3e2ee"
        m.layers.append(land_layer())
        if not args.top:
            add_country_layers(m, info)
        m.layers.append(boundaries_layer())
        m.layers.append(land_boundaries_layer())
        if args.top:
            add_country_layers(m, info)
        m.layers.append(lakes_layer())
    return m

# The main script

out_format = "png256" if args.png8 else "png"

m = create_base_map(data, width, height)
render_map(m, os.path.join(args.out, "a.png"), 
           out_format=out_format, scale=args.scale, debug=args.debug)

if args.test:
    print("done (test)")
    exit(0)

def check_name(name):
    if not args.countries:
        return True
    for x in args.countries:
        if name.startswith(x):
            return True
    return False

for country in countries:
    name = country.name
    if not check_name(name):
        continue
    print("Processing: {0}".format(name))
    m = create_map(data, width, height, country)
    out_name = os.path.join(args.out, "{0}.png".format(country.out_name))
    render_map(m, out_name, out_format=out_format, scale=args.scale, debug=args.debug)

print("done")
