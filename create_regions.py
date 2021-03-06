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

cities_file_50m = os.path.join(cult50m_dir, 'ne_50m_populated_places.shp')
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

cities_file_10m = os.path.join(cult10m_dir, 'ne_10m_populated_places.shp')
#land_file_10m = os.path.join(phys10m_dir, 'ne_10m_land.shp')
land_file_10m = os.path.join(cult10m_dir, 'ne_10m_admin_0_sovereignty.shp')
land_boundaries_file_10m = os.path.join(phys10m_dir, 'ne_10m_land.shp')
boundaries_file_10m = os.path.join(edited10m_dir, 'ne_10m_admin_0_boundary_lines_land.shp')
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

parser.add_argument('--cities',
                    help="input JSON data file for cities")

parser.add_argument('--capitals', action='store_true',
                    help="select capitals only")

parser.add_argument('--region-capitals', action='store_true',
                    help="select regional capitals only")

parser.add_argument('--marker-size', type=float, default=8.0,
                    help="marker size for cities")

parser.add_argument('--border', type=float, default=1.8,
                    help="marker border width for cities (0 = no border)")

parser.add_argument('--border-color', default='black',
                    help="marker border color for cities")

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

parser.add_argument('--region-only', action='store_true',
                    help="render region polygons only")

parser.add_argument('--land-only', action='store_true',
                    help="render the land layer only")

parser.add_argument('--base-map-only', action='store_true',
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
        self.code = None
        self.more = []
        if isinstance(data, str):
            self.name = data
        else:
            assert(isinstance(data, dict))
            self.name = data['name']
            if 'more' in data:
                self.more = [s for s in data['more']]
            if 'code' in data:
                self.code = data['code']
            if 'out' in data:
                self.out_name = data['out']
            if 'marker-size' in data:
                self.marker_size = tuple(data['marker-size'])
            if 'marker-offset' in data:
                self.marker_offset = tuple(data['marker-offset'])
        if not self.out_name:
            self.out_name = self.name

regions = []
for region in data['regions']:
    regions.append(RegionInfo(region))

class CityInfo:
    def __init__(self, data):
        try:
            self.marker_size = None
            self.marker_offset = None
            self.out_name = None
            if isinstance(data, str):
                self.name = data
            else:
                assert(isinstance(data, dict))
                self.name = data['name']
                if 'out' in data:
                    self.out_name = data['out']
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
if args.cities:
    with open(args.cities) as f:
        cities_data = json.load(f)
    for city in cities_data['cities']:
        info = CityInfo(city)
        cities.append(info)
        cities_dict[info.name] = info


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

if 'regions-file' in data:
    regions_file = data['regions-file']

if 'region-boundaries-file' in data:
    region_boundaries_file = data['region-boundaries-file']

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
    if 'out' in data:
        out_name = data['out']
    else:
        out_name = data['admin']
    args.out = "out_{0}_{1}_{2}".format(out_name, width, height)

if not os.path.exists(args.out):
    os.makedirs(args.out)

if not os.path.isdir(args.out):
    report_error("The output path is not a directory: {0}".format(args.out))
    sys.exit(1)

def escape(s):
    return s.replace("'", "\\'").replace('"', '\\"')

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

#    stk = Stroke(Color('#A0A0A0'), 1.0)
    ls = LineSymbolizer()
    ls.stroke = Color('#A0A0A0')
    ls.stroke_width = 1.0
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

#    stk = Stroke(Color('#4fadc2'), 1.0)
    ls = LineSymbolizer()
    ls.stroke = Color('#4fadc2')
    ls.stroke_width = 1.0
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

#    stk = Stroke(Color('#4fadc2'), 1.0)
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

def boundaries_style(admin=None):
    s = Style()
    r = Rule()

    ls = LineSymbolizer()
    ls.stroke = Color('black')
#    stk = Stroke()
#    stk.color = Color('black')

    if admin:
        r.filter = Expression("[adm0_left] = '{0}' or [adm0_right] = '{0}'".format(admin))
        ls.stroke_width = 2.0
    else:
        ls.stroke_width = 1.0

    # stk = Stroke()
    # stk.add_dash(8, 4)
    # stk.add_dash(2, 2)
    # stk.add_dash(2, 2)
    # stk.color = Color('black')
    # stk.width = 3.0
    # ls = LineSymbolizer(stk)
    # r.symbols.append(ls)

#    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    s.rules.append(r)
    return s

def boundaries_layer():
    ds = Shapefile(file=boundaries_file)
    layer = Layer('Boundaries')
    layer.datasource = ds
    return layer

# Boundaries of regions

def region_boundaries_style(admin, region=None):
    s = Style()
    r = Rule()

    filter_str = "[adm0_name] = '{0}'".format(admin)
    if region:
        filter_str += " and ([name_l] = '{0}' or [name_r] = '{0}')".format(region)
    
    r.filter = Expression(filter_str)

#    stk = Stroke(Color('#808080'), 1.5)
    ls = LineSymbolizer()
    ls.stroke = Color('#808080')
    ls.stroke_width = 1.5
    r.symbols.append(ls)

    s.rules.append(r)
    return s

def region_boundaries_layer():
    ds = Shapefile(file=region_boundaries_file)
    layer = Layer('Region Boundaries')
    layer.datasource = ds
    return layer

# Regions

def region_style(admin, name, code=None, more=[], boundary_flag=False):
    s = Style()
    r = Rule()

    filter_str = "[admin] = '{0}'".format(admin)
    if code:
        filter_str += " and ([adm1_code] = '{0}'".format(code)
    else:
        filter_str += " and ([name] = '{0}'".format(name)

    if more:
        filter_str += "".join([" or [name] = '{0}'".format(t) for t in more])

    filter_str += ")"

    r.filter = Expression(filter_str)

    if args.color:
        ps = PolygonSymbolizer()
        ps.fill = Color(args.color)
        r.symbols.append(ps)

    if boundary_flag:
#        stk = Stroke(Color('black'), 1.5)
        ls = LineSymbolizer()
        ls.stroke = Color('black')
        ls.stroke_width = 1.5
        r.symbols.append(ls)
    elif more and args.color:
#        stk = Stroke(Color(args.color), 0.5)
        ls = LineSymbolizer()
        ls.stroke = Color(args.color)
        ls.stroke_width = 0.5
        r.symbols.append(ls)

    s.rules.append(r)
    return s

def region_layer(name):
    ds = Shapefile(file=regions_file)
    layer = Layer("Region " + name)
    layer.datasource = ds
    return layer

def tiny_style(admin, name, code=None, size=(10,10), offset=None):
    s = Style()
    r = Rule()

    if code:
        r.filter = Expression("[admin] = '{0}' and [adm1_code] = '{1}'".format(admin, code))
    else:
        r.filter = Expression("[admin] = '{0}' and [name] = '{1}'".format(admin, name))

    ms = MarkersSymbolizer()
    ms.fill = Color('red')
    ms.opacity = 0.4
#    ms.stroke = Stroke(Color('black'), 0.0)
    ms.stroke = Color('black')
    ms.stroke_width = 0.0
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


# Base map

def base_map(data, width, height):
    m = Map(width, height, data['proj'])
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
    elif args.region_only:
        pass
    else:
        m.background = Color('#b3e2ee')
        add_layer_with_style(m, land_layer(),
                             land_style(), 'Land Style')
        add_layer_with_style(m, admin_layer(),
                             admin_style(admin), 'Admin Style')
        add_layer_with_style(m, region_boundaries_layer(),
                             region_boundaries_style(admin), 'Region Boundaries Style')
        if args.all_boundaries:
            add_layer_with_style(m, boundaries_layer(),
                                 boundaries_style(), 'All Boundaries Style')
        add_layer_with_style(m, boundaries_layer(),
                             boundaries_style(admin), 'Boundaries Style')
        add_layer_with_style(m, land_boundaries_layer(),
                             land_boundaries_style(), 'Land Boundaries Style')
        add_layer_with_style(m, lakes_layer(),
                             lakes_style(), 'Lakes Style')
    if cities:
        city_names = set([city.name for city in cities])
        add_layer_with_style(m, cities_layer(city_names), 
                     cities_style(city_names, size=args.marker_size), 'All Cities')


    m.zoom_to_box(Box2d(*data['bbox']))
    return m

# A map with a region

def set_region(m, admin, info):
    style = region_style(admin, info.name, code=info.code, more=info.more,
                         boundary_flag=args.region_only)
    layer = region_layer(info.name)
    style_name = 'Style ' + info.name
    m.append_style(style_name, style)
    layer.styles.append(style_name)

    if args.admin_only:
        pos = 2 if args.top else 1
        max_pos = 3
    elif args.region_only:
        pos = 0
        max_pos = 0
    elif args.all_boundaries:
        pos = 6 if args.top else 4
        max_pos = 7
    else:
        pos = 5 if args.top else 3
        max_pos = 6

    while len(m.layers) > max_pos:
        del m.layers[pos]

    m.layers[pos:pos] = layer

    if info.marker_size and not args.no_markers:
        style = tiny_style(admin, info.name, code=info.code, 
                           size=info.marker_size, offset=info.marker_offset)
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

if args.base_map_only:
    print("done (base map only)")
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
