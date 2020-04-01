# 50m maps of all states (10m Alaska shape)

import os
import sys
import argparse
from mapnik_xml import *

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
coords_48 = (-2507299.94,-1797501.58,2291598.94,1801672.58)
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

parser.add_argument('--suffix', default="-map",
                    help="the suffix for output image names")

parser.add_argument('--out', dest="out_dir", metavar='DIR',
                    help="the output directory")

parser.add_argument('--color', default='red',
                    help="polygon fill color (use 'none' for no color)")

parser.add_argument('--no-border', action='store_true',
                    help="do no render borders and the background")

#parser.add_argument('--line-color', default='black',
#                    help="border line color (use 'none' for no borders)")

parser.add_argument('--scale', type=float, default=1.0,
                    help="scale for lines")

parser.add_argument('states', nargs='*',
                    help="create images for given states only")

parser.add_argument('--debug', action='store_true',
                    help="debug mode")


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

print("Size: {0} x {1}, scale: {2}".format(width, height, args.scale))


# Land

def land_layer():
    s = Style("Land")
    s.symbols.append(PolygonSymbolizer('#f1daa0'))
    return Layer("Land", land_file, s)

# USA

def usa_layer():
    s = Style("USA")
    s.filter = "[admin] = 'United States of America'"
    s.symbols.append(PolygonSymbolizer('white'))
    return Layer("USA", countries_file, s)

# Land boundaries

def land_boundaries_layer():
    s = Style("Land Boundaries")
    s.symbols.append(LineSymbolizer('#4fadc2', 1.5))
    return Layer("Land Boundaries", land_boundaries_file, s)

# State boundaries

def state_boundaries_layer():
    s = Style("State Boundaries")
    s.filter = "[adm0_name] = 'United States of America'"
    s.symbols.append(LineSymbolizer('#808080', 1.5))
    return Layer("State Boundaries", state_boundaries_file, s)

# Lakes

def lakes_layer():
    s = Style("Lakes")
    s.filter = "[scalerank] <= {0}".format(lakes_size)
    s.symbols.append(PolygonSymbolizer('#b3e2ee'))
    s.symbols.append(LineSymbolizer('#4fadc2', 1.5))
    return Layer("Lakes", lakes_file, s)

# Boundaries of countries

def country_boundaries_layer():
    s = Style("Country Boundaries")
    ls = LineSymbolizer('black', 3.0)
    ls.add_dash(8, 4)
    ls.add_dash(2, 2)
    ls.add_dash(2, 2)
    s.symbols.append(ls)
    return Layer("Country Boundaries", country_boundaries_file, s)

# A state

def state_layer(state_abbrev, flag10=False):
    s = Style(state_abbrev)
    s.filter = "[iso_3166_2] = 'US-{0}'".format(state_abbrev.upper())
    if args.color:
        ps = PolygonSymbolizer(args.color)
        s.symbols.append(ps)
    ds = states10m_file if flag10 else states50m_file
    return Layer(state_abbrev, ds, s)

# Main map functions

def create_map(proj, coords, width, height):
    m = Map(width, height, proj, coords)
    if args.no_border:
        m.layers.append(land_layer())
        m.layers.append(usa_layer())
        m.layers.append(lakes_layer())
    else:
        #m.background = '#b3e2ee80'
        m.background = '#b3e2ee'
        m.layers.append(land_layer())
        m.layers.append(usa_layer())
        m.layers.append(land_boundaries_layer())
        m.layers.append(state_boundaries_layer())
        m.layers.append(lakes_layer())
        m.layers.append(country_boundaries_layer())
    return m

def render_states(m, states, subdir=None, suffix=""):
    for state in states:
        print("Processing: {0}".format(state))

        if args.no_border:
            pos = 2
            while len(m.layers) > 3:
                del m.layers[pos]
        else:
            pos = 3
            while len(m.layers) > 6:
                del m.layers[pos]

        layer = state_layer(state, flag10=(state == 'AK'))
        m.layers[pos:pos] = [layer]

        out_name = '{0}{1}.png'.format(state.lower(), suffix)
        out_path = os.path.join(subdir, out_name) if subdir else out_name
        render_map(m, os.path.join(args.out_dir, out_path),
                    out_format=out_format, scale=args.scale, debug=args.debug)

# The main script

map_48 = create_map(proj4_usa, coords_48, width, height)
map_ne = create_map(proj4_usa, coords_ne, width, height)
map_all = create_map(proj4_usa, coords_all, width, height)

render_map(map_48, os.path.join(args.out_dir, '48', 'a.png'), 
    out_format=out_format, scale=args.scale, debug=args.debug)

render_map(map_ne, os.path.join(args.out_dir, 'ne', 'a.png'), 
    out_format=out_format, scale=args.scale, debug=args.debug)

render_map(map_all, os.path.join(args.out_dir, 'all', 'a.png'), 
    out_format=out_format, scale=args.scale, debug=args.debug)

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

# Render states
render_states(map_48, set(states) - set(ne_states + far_states), subdir="48", suffix=args.suffix)

# Render northeastern states
print("\nRendering northeastern states")
render_states(map_ne, ne_states, subdir="ne", suffix=args.suffix)

# Render Alaska and Hawaii
print("\nRendering Alaska and Hawaii")
render_states(map_all, far_states, subdir="all", suffix=args.suffix)

print("done")
