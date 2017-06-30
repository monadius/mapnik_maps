import os
import sys
import argparse
import json

# Global variables

base_dir = '/Users/monad/Work/data'

cult10m_dir = os.path.join(base_dir, '10m_cultural', '10m_cultural')
phys10m_dir = os.path.join(base_dir, '10m_physical')
edited10m_dir = os.path.join(base_dir, 'edited10m')

cult50m_dir = os.path.join(base_dir, '50m_cultural')
phys50m_dir = os.path.join(base_dir, '50m_physical')
edited50m_dir = os.path.join(base_dir, 'edited50m')

# 50m data files

land_file_50m = os.path.join(phys50m_dir, 'ne_50m_land.shp')
#land_boundaries_file_50m = os.path.join(phys50m_dir, 'ne_50m_land.shp')
land_boundaries_file_50m = os.path.join(phys50m_dir, 'ne_50m_coastline.shp')
#land_boundaries_file_50m = os.path.join(edited50m_dir, 'ne_50m_coastline_edited.shp')
#boundaries_file_50m = os.path.join(cult50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp')
boundaries_file_50m = os.path.join(edited50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp')
countries_file_50m = os.path.join(cult50m_dir, 'ne_50m_admin_0_countries.shp')
lakes_file_50m = os.path.join(phys50m_dir, 'ne_50m_lakes.shp')

land_file_50m = countries_file_50m

# 10m data files

#land_file_10m = os.path.join(phys10m_dir, 'ne_10m_land.shp')
land_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_sovereignty.shp')
land_boundaries_file_10m = os.path.join(phys10m_dir, 'ne_10m_land.shp')
boundaries_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_boundary_lines_land.shp')
countries_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_countries.shp')
lakes_file_10m = os.path.join(phys10m_dir, 'ne_10m_lakes.shp')

#disputed_file = os.path.join(cult50m_dir, 'ne_50m_admin_0_breakaway_disputed_areas.shp')

regions_file = os.path.join(cult10m_dir, 'ne_10m_admin_1_states_provinces_shp.shp')
region_boundaries_file = os.path.join(edited10m_dir, 'ne_10m_admin_1_states_provinces_lines.shp')
tiny_file = regions_file

def report_error(msg):
    sys.stderr.write("\n**ERROR**: {0}\n\n".format(msg))

# Command line arguments
    
parser = argparse.ArgumentParser(description="Creates a specific country map with regions")

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
                    help="polygon fill color for regions (use 'none' for no color)")

#parser.add_argument('--line-color', default='black',
#                    help="border line color (use 'none' for no borders)")

parser.add_argument('--scale', type=float, default=1.0,
                    help="scale for lines")

parser.add_argument('--lakes-size', type=int, default=3,
                    help="the size of rendered lakes (0 = no lakes, 1 = largest lakes, etc.)")

parser.add_argument('--no-markers', action='store_true',
                    help="do not draw markers")

parser.add_argument('--top', action='store_true',
                    help="move the regions layer above the land boundary layer")

parser.add_argument('--admin-only', action='store_true',
                    help="render the main country only")

parser.add_argument('--all-boundaries', action='store_true',
                    help="render all boundaries between countries")

parser.add_argument('--land-only', action='store_true',
                    help="render the land layer only")

parser.add_argument('--test', action='store_true',
                    help="produce one map only")

parser.add_argument('input_file',
                    help="input JSON data file")

parser.add_argument('regions', nargs='*',
                    help="a list of regions (if empty then maps for all regions in the input data file are created)")

# Parse arguments and load the input file

args = parser.parse_args()

with open(args.input_file) as f:
    data = json.load(f)

class RegionInfo:
    def __init__(self, data):
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
        if not self.out_name:
            self.out_name = self.name

regions = []
for region in data['regions']:
    regions.append(RegionInfo(region))
                
# Validate data

if 'admin' not in data:
    report_error("'admin' is not defined in {0}".format(args.input_file))
    exit(2)

#admin = data['admin']

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
#print("offset-scales = {0} {1}".format(offset_scale_x, offset_scale_y))

if args.color == 'none':
    args.color = None

#if args.line_color == 'none':
#    args.line_color = None
    
if args.scale < 0.01 or args.scale > 10:
    report_error("Bad scale: {0}".format(args.scale))
    sys.exit(1)
    
if width < 1 or height < 1 or width > 10000 or height > 10000:
    report_error("Bad image size: {0} x {1}".format(width, height))
    sys.exit(1)
    
if not args.out:
    args.out = "out_{0}_{1}_{2}".format(data['admin'], width, height)

if not os.path.exists(args.out):
    os.makedirs(args.out)

if not os.path.isdir(args.out):
    report_error("The output path is not a directory: {0}".format(args.out))
    sys.exit(1)

# Styles and layers

# Land

def add_layer_with_style(m, layer, style, style_name=None):
    if not style_name:
        style_name = layer.name + 'Style'
    m.append_style(style_name, style)
    layer.styles.append(style_name)
    m.layers.append(layer)

def land_style():
    s = Style()
    r = Rule()

    ps = PolygonSymbolizer()
    ps.fill = Color('#f1daa0')
    r.symbols.append(ps)

#    stk = Stroke(Color('#4fadc2'), 5.0)
#    ls = LineSymbolizer(stk)
#    r.symbols.append(ls)

    s.rules.append(r)
    return s

def land_layer():
    ds = Shapefile(file=land_file)    
    layer = Layer('Land')
    layer.datasource = ds
    return layer
    
# Admin (country)

def admin_style(admin):
    s = Style()
    r = Rule()

    r.filter = Expression("[admin] = '{0}'".format(admin))

    ps = PolygonSymbolizer()
    ps.fill = Color('white')
    r.symbols.append(ps)

    s.rules.append(r)
    return s

def admin_style_with_boundary(admin):
    s = Style()
    r = Rule()

    r.filter = Expression("[admin] = '{0}'".format(admin))

    ps = PolygonSymbolizer()
    ps.fill = Color('white')
    r.symbols.append(ps)

    stk = Stroke(Color('#A0A0A0'), 1.0)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    s.rules.append(r)
    return s    

def admin_layer():
    ds = Shapefile(file=countries_file)
    layer = Layer('Admin (country)')
    layer.datasource = ds
    return layer

# Land boundaries

def land_boundaries_style():
    s = Style()
    r = Rule()

    stk = Stroke(Color('#4fadc2'), 1.0)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

#    ps = PolygonSymbolizer()
#    ps.fill = Color('red')
#    r.symbols.append(ps)

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

    r.filter = Expression("[scalerank] <= {0}".format(args.lakes_size))

    ps = PolygonSymbolizer()
    ps.fill = Color('#b3e2ee')
    r.symbols.append(ps)

    stk = Stroke(Color('#4fadc2'), 1.0)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    s.rules.append(r)
    return s

def lakes_layer():
    ds = Shapefile(file=lakes_file)
    layer = Layer('Lakes')
    layer.datasource = ds
    return layer

# Boundaries of countries

def boundaries_style(admin=None):
    s = Style()
    r = Rule()

    if admin:
        r.filter = Expression("[adm0_left] = '{0}' or [adm0_right] = '{0}'".format(admin))

    # stk = Stroke()
    # stk.add_dash(8, 4)
    # stk.add_dash(2, 2)
    # stk.add_dash(2, 2)
    # stk.color = Color('black')
    # stk.width = 3.0
    # ls = LineSymbolizer(stk)
    # r.symbols.append(ls)

    stk = Stroke()
    stk.color = Color('black')
    stk.width = 2.0
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    s.rules.append(r)
    return s

def boundaries_layer():
    ds = Shapefile(file=boundaries_file)
    layer = Layer('Boundaries')
    layer.datasource = ds
    return layer

# Boundaries of regions

def region_boundaries_style(admin):
    s = Style()
    r = Rule()

    r.filter = Expression("[adm0_name] = '{0}'".format(admin))

    stk = Stroke(Color('#808080'), 1.5)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    s.rules.append(r)
    return s

def region_boundaries_layer():
    ds = Shapefile(file=region_boundaries_file)
    layer = Layer('Region Boundaries')
    layer.datasource = ds
    return layer

# Regions

def region_style(admin, name):
    s = Style()
    r = Rule()

    r.filter = Expression("[admin] = '{0}' and [name] = '{1}'".format(admin, name))

    if args.color:
        ps = PolygonSymbolizer()
        ps.fill = Color(args.color)
        r.symbols.append(ps)

    s.rules.append(r)
    return s

def region_layer(name):
    ds = Shapefile(file=regions_file)
    layer = Layer("Region " + name)
    layer.datasource = ds
    return layer

def tiny_style(admin, name, size=(10,10), offset=None):
    s = Style()
    r = Rule()

    r.filter = Expression("[admin] = '{0}' and [name] = '{1}'".format(admin, name))

    ms = MarkersSymbolizer()
    ms.fill = Color('red')
    ms.opacity = 0.4
    ms.stroke = Stroke(Color('black'), 0.0)
    ms.width = Expression('{0}'.format(size[0] * args.scale))
    ms.height = Expression('{0}'.format(size[1] * args.scale))
    if offset:
        ms.transform = 'translate({0}, {1})'.format(offset[0] * offset_scale_x, offset[1] * offset_scale_y)
    r.symbols.append(ms)

    s.rules.append(r)
    return s

def tiny_layer(name):
    ds = Shapefile(file=tiny_file)
    layer = Layer("Tiny " + name)
    layer.datasource = ds
    return layer

# Base map

def base_map(data, width, height):
    m = Map(width, height, data['proj'].encode())
    admin = data['admin']
    if args.admin_only:
        add_layer_with_style(m, admin_layer(),
                             admin_style_with_boundary(admin), 'Admin Style')
        add_layer_with_style(m, region_boundaries_layer(),
                             region_boundaries_style(admin), 'Region Boundaries Style')
        add_layer_with_style(m, lakes_layer(),
                             lakes_style(), 'Lakes Style')
    elif args.land_only:
        add_layer_with_style(m, land_layer(),
                             land_style(), 'Land Style')
        add_layer_with_style(m, admin_layer(),
                             admin_style(admin), 'Admin Style')
    else:
        m.background = Color('#b3e2ee')
        add_layer_with_style(m, land_layer(),
                             land_style(), 'Land Style')
        add_layer_with_style(m, admin_layer(),
                             admin_style(admin), 'Admin Style')
        add_layer_with_style(m, region_boundaries_layer(),
                             region_boundaries_style(admin), 'Region Boundaries Style')
        add_layer_with_style(m, boundaries_layer(),
                             boundaries_style(None if args.all_boundaries else admin), 
                             'Boundaries Style')
        add_layer_with_style(m, land_boundaries_layer(),
                             land_boundaries_style(), 'Land Boundaries Style')
        add_layer_with_style(m, lakes_layer(),
                             lakes_style(), 'Lakes Style')
    m.zoom_to_box(Box2d(*data['bbox']))
    return m

# A map with a region

def set_region(m, admin, info):
    style = region_style(admin, info.name)
    layer = region_layer(info.name)
    style_name = 'Style ' + info.name
    m.append_style(style_name, style)
    layer.styles.append(style_name)

    if args.admin_only:
        pos = 2 if args.top else 1
        max_pos = 3
    else:
        pos = 5 if args.top else 3
        max_pos = 6

    while len(m.layers) > max_pos:
        del m.layers[pos]
    
    m.layers[pos:pos] = layer

    if info.marker_size and not args.no_markers:
        style = tiny_style(admin, info.name, size=info.marker_size, offset=info.marker_offset)
        layer = tiny_layer(info.name)
        style_name = 'Tiny Style ' + info.name
        m.append_style(style_name, style)
        layer.styles.append(style_name)
        m.layers[pos+1:pos+1] = layer

# The main script

from mapnik import *

out_format = 'png256' if args.png8 else 'png'

admin = data['admin']
m = base_map(data, width, height)
render_to_file(m, os.path.join(args.out, 'a.png'), out_format, args.scale)

if args.test:
    print("done (test)")
    exit(0)

def check_name(name):
    if not args.regions:
        return True
    for x in args.regions:
        if name.startswith(x):
            return True
    return False

for region in regions:
    name = region.name
    if not check_name(name):
        continue
    print("Processing: {0}".format(name))
    set_region(m, admin, region)
    out_name = os.path.join(args.out, "{0}.png".format(region.out_name))
    render_to_file(m, out_name, out_format, args.scale)

print("done")
