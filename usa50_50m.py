# 50m maps of all states (10m Alaska shape)

import os
import sys
import argparse

# Global variables

xd_width, xd_height = 1200, 900

base_dir = '/Users/monad/Work/data'
cult10m_dir = os.path.join(base_dir, '10m_cultural', '10m_cultural')
phys10m_dir = os.path.join(base_dir, '10m_physical')
cult50m_dir = os.path.join(base_dir, '50m_cultural')
phys50m_dir = os.path.join(base_dir, '50m_physical')

land_file = os.path.join(phys50m_dir, 'ne_50m_land.shp')
land_boundaries_file = os.path.join(phys50m_dir, 'ne_50m_land.shp')
countries_file = os.path.join(cult50m_dir, 'ne_50m_admin_0_countries.shp')
state_boundaries_file = os.path.join(cult50m_dir, 'ne_50m_admin_1_states_provinces_lines.shp')
lakes_file = os.path.join(phys50m_dir, 'ne_50m_lakes.shp')
country_boundaries_file = os.path.join(cult50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp')

states10m_file = os.path.join(cult10m_dir, 'ne_10m_admin_1_states_provinces_shp.shp')
states50m_file =os.path.join(cult50m_dir, 'ne_50m_admin_1_states_provinces_shp.shp')

#land_file = os.path.join(phys10m_dir, 'ne_10m_land.shp')
#land_file = os.path.join(cult10m_dir, 'ne_10m_admin_0_sovereignty.shp')
#land_boundaries_file = os.path.join(phys10m_dir, 'ne_10m_land.shp')
#boundaries_file = os.path.join(cult10m_dir, 'ne_10m_admin_0_boundary_lines_land.shp')
#boundaries_file = os.path.join(edited50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp')
#countries_file = os.path.join(cult10m_dir, 'ne_10m_admin_0_countries.shp')
#lakes_file = os.path.join(phys10m_dir, 'ne_10m_lakes.shp')

lakes_size = 3

proj4_usa = '+proj=lcc +lat_1=33 +lat_2=45 +lat_0=39 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'
coords_48 = (-2607277,-1554066,2391576,1558237)
zoom_48 = 0.96
coords_ne = (230348, -289948,2331777,1276571)
coords_all = (-6377775,-2106929,2244702,4808764)

def report_error(msg):
    sys.stderr.write("**ERROR**: {0}\n".format(msg))

parser = argparse.ArgumentParser(description="Creates maps for all 50 states")

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

parser.add_argument('--out', dest='out_dir', metavar='DIR',
                    help="the output directory")

parser.add_argument('--color', default='red',
                    help="polygon fill color (use 'none' for no color)")

#parser.add_argument('--line-color', default='black',
#                    help="border line color (use 'none' for no borders)")

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

#if args.line_color == 'none':
#    args.line_color = None
    
if args.scale < 0.01 or args.scale > 10:
    report_error("Bad scale: {0}".format(args.scale))
    sys.exit(1)
    
if width < 1 or height < 1 or width > 10000 or height > 10000:
    report_error("Bad image size: {0} x {1}".format(width, height))
    sys.exit(1)
    
if not args.out_dir:
    args.out_dir = "out_maps_of_states_{0}_{1}".format(width, height)

if not os.path.exists(args.out_dir):
    os.makedirs(args.out_dir)

out_format = 'png256' if args.png8 else 'png'


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

# USA

def usa_style():
    s = Style()
    r = Rule()

    r.filter = Expression("[admin] = 'United States of America'")

    ps = PolygonSymbolizer()
    ps.fill = Color('white')
    r.symbols.append(ps)

    s.rules.append(r)
    return s

def usa_layer():
    ds = Shapefile(file=countries_file)
    layer = Layer('USA')
    layer.datasource = ds
    return layer

# Land boundaries

def land_boundaries_style():
    s = Style()
    r = Rule()

#    r.filter = Expression("[admin] = 'United States of America'")

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

# State boundaries

def state_boundaries_style():
    s = Style()
    r = Rule()

    r.filter = Expression("[adm0_name] = 'United States of America'")

    stk = Stroke(Color('#808080'), 1.0)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    s.rules.append(r)
    return s

def state_boundaries_layer():
    ds = Shapefile(file=state_boundaries_file)
    layer = Layer('State Boundaries')
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

def country_boundaries_style():
    s = Style()
    r = Rule()

    stk = Stroke()
    stk.add_dash(8, 4)
    stk.add_dash(2, 2)
    stk.add_dash(2, 2)
    stk.color = Color('black')
    stk.width = 2.0
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    s.rules.append(r)
    return s

def country_boundaries_layer():
    ds = Shapefile(file=country_boundaries_file)
    layer = Layer('Country Boundaries')
    layer.datasource = ds
    return layer

# A state

def state_style(state_abbrev):
    s = Style()
    r = Rule()

    r.filter = Expression("[iso_3166_2] = 'US-{0}'".format(state_abbrev.upper()))

    if args.color:
        ps = PolygonSymbolizer()
        ps.fill = Color(args.color)
        r.symbols.append(ps)

    s.rules.append(r)
    return s

def state_layer(state_abbrev, flag10=False):
    if flag10:
        ds = Shapefile(file=states10m_file)
    else:
        ds = Shapefile(file=states50m_file)
    layer = Layer(state_abbrev)
    layer.datasource = ds
    return layer

# Main map functions

def create_map(proj, coords, width, height, zoom=None):
    m = Map(width, height, proj)
    #m.background = Color('#b3e2ee80')
    m.background = Color('#b3e2ee')
    add_layer_with_style(m, land_layer(), land_style())
    add_layer_with_style(m, usa_layer(), usa_style())
    add_layer_with_style(m, land_boundaries_layer(), land_boundaries_style())
    add_layer_with_style(m, state_boundaries_layer(), state_boundaries_style())
    add_layer_with_style(m, lakes_layer(), lakes_style())
    add_layer_with_style(m, country_boundaries_layer(), country_boundaries_style())
    m.zoom_to_box(Box2d(*coords))
    if zoom:
        m.zoom(zoom)
    return m

def render_states(m, states, prefix="", suffix=""):
    for state in states:
        print("Processing: {0}".format(state))
        
        while len(m.layers) > 6:
            del m.layers[3]

        style = state_style(state)
        layer = state_layer(state, flag10=(state == 'AK'))
        style_name = layer.name + 'Style'
        m.append_style(style_name, style)
        layer.styles.append(style_name)
        m.layers[3:3] = layer

        out_name = '{0}{1}{2}.png'.format(prefix, state, suffix)
        render_to_file(m, os.path.join(args.out_dir, out_name),
                       out_format, args.scale)

# The main script

from mapnik import *

map_48 = create_map(proj4_usa, coords_48, width, height, zoom=zoom_48)
map_ne = create_map(proj4_usa, coords_ne, width, height)
map_all = create_map(proj4_usa, coords_all, width, height)

render_to_file(map_48, os.path.join(args.out_dir, 'a_48.png'),
               out_format, args.scale) 

render_to_file(map_ne, os.path.join(args.out_dir, 'a_ne.png'),
               out_format, args.scale)

render_to_file(map_all, os.path.join(args.out_dir, 'a_all.png'),
               out_format, args.scale)

# Render states

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD',
          'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH',
          'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
          'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

ne_states = ['CT', 'DE', 'MA', 'MD', 'NH', 'NJ', 'RI', 'VT']

far_states = ['AK', 'HI']

if args.states:
    test = lambda s: s in args.states
    states = filter(test, states)
    ne_states = filter(test, ne_states)
    far_states = filter(test, far_states)

# Render all states (48 visible)
render_states(map_48, states)

# Render northeastern states
print("\nRendering northeastern states")
render_states(map_ne, ne_states, prefix="ne_")

# Render Alaska and Hawaii
print("\nRendering Alaska and Hawaii")
render_states(map_all, far_states, prefix="all_")

print("done")
