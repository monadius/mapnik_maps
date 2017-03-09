import os
from mapnik import *

base_dir = '/Users/monad/Work/data'
out_dir = 'out_usa50_10m'
cult10m_dir = os.path.join(base_dir, '10m_cultural', '10m_cultural')
phys10m_dir = os.path.join(base_dir, '10m_physical')

proj4_usa = '+proj=lcc +lat_1=33 +lat_2=45 +lat_0=39 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'
#proj4_usa = '+proj=lcc +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

m = Map(1200, 900, proj4_usa)
#m.background = Color('#b3e2ee80')
m.background = Color('#b3e2ee')


# Land

def land_style():
    s = Style()
    r = Rule()

    ps = PolygonSymbolizer()
    ps.fill = Color('#f1daa0')
    r.symbols.append(ps)

    name = 'LandStyle'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def land_layer():
#    ds = Shapefile(file=os.path.join(phys10m_dir, 'ne_10m_land.shp'))
    ds = Shapefile(file=os.path.join(cult10m_dir, 'ne_10m_admin_0_countries.shp'))    
    layer = Layer('Land1')
    layer.datasource = ds
    layer.styles.append(land_style())
    return layer


# USA

def usa_style():
    s = Style()
    r = Rule()

    r.filter = Expression("[admin] = 'United States of America'")

    ps = PolygonSymbolizer()
    ps.fill = Color('white')
    r.symbols.append(ps)

    name = 'USAStyle'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def usa_layer():
    ds = Shapefile(file=os.path.join(cult10m_dir, 'ne_10m_admin_0_countries.shp'))
    layer = Layer('USA')
    layer.datasource = ds
    layer.styles.append(usa_style())
    return layer


# Land boundaries

def land_boundaries_style():
    s = Style()
    r = Rule()

#    r.min_scale = 0
#    r.max_scale = 1e+10
    
    stk = Stroke(Color('#4fadc2'), 1.0)
    stk.opacity = 1.0
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

#    ls = LineSymbolizer(Color('red'), 2.0)
#    r.symbols.append(ls)

    name = 'LandBoundariesStyle'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def land_boundaries_layer():
    ds = Shapefile(file=os.path.join(phys10m_dir, 'ne_10m_land.shp'))    
#    ds = Shapefile(file=os.path.join(cult10m_dir, 'ne_10m_admin_0_countries.shp'))
    layer = Layer('LandBoundaries')
    layer.datasource = ds
    layer.styles.append(land_boundaries_style())
    return layer


# State boundaries

def states_style():
    s = Style()
    r = Rule()

    r.filter = Expression("[adm0_name] = 'United States of America'")

    stk = Stroke(Color('#808080'), 1.0)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    name = 'States Style'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def states_layer():
    ds = Shapefile(file=os.path.join(cult10m_dir, 'ne_10m_admin_1_states_provinces_lines_shp.shp'))
    layer = Layer('States')
    layer.datasource = ds
    layer.styles.append(states_style())
    return layer


# Lakes

def lakes_style():
    s = Style()
    r = Rule()

    r.filter = Expression("[scalerank] <= 3")

    ps = PolygonSymbolizer()
    ps.fill = Color('#b3e2ee')
    r.symbols.append(ps)

    stk = Stroke(Color('#4fadc2'), 1.0)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    name = 'Lakes Style'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def lakes_layer():
    ds = Shapefile(file=os.path.join(phys10m_dir, 'ne_10m_lakes.shp'))
    layer = Layer('Lakes')
    layer.datasource = ds
    layer.styles.append(lakes_style())
    return layer


# Boundaries of countries

def admin_0_boundaries_style():
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

    name = 'Admin 0 Boundaries Style'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def admin_0_boundaries_layer():
    ds = Shapefile(file=os.path.join(cult10m_dir, 'ne_10m_admin_0_boundary_lines_land.shp'))
    layer = Layer('Admin 0 Boundaries')
    layer.datasource = ds
    layer.styles.append(admin_0_boundaries_style())
    return layer


# A state

def state_style(state_name):
    name = 'State Style ' + state_name

    s = Style()
    r = Rule()

    r.filter = Expression("[iso_3166_2] = 'US-{0}'".format(state_name))

    ps = PolygonSymbolizer()
    ps.fill = Color('red')
    r.symbols.append(ps)

    s.rules.append(r)
    m.append_style(name, s)
    return name

def state_layer(state_name):
    ds = Shapefile(file = os.path.join(cult10m_dir, 'ne_10m_admin_1_states_provinces_shp.shp'))
    layer = Layer(state_name)
    layer.datasource = ds
    layer.styles.append(state_style(state_name))
    return layer


# Create and add all layers

m.layers.append(land_layer())
m.layers.append(usa_layer())
m.layers.append(land_boundaries_layer())

#m.layers.append(state_layer('AK'))

m.layers.append(states_layer())
m.layers.append(lakes_layer())
m.layers.append(admin_0_boundaries_layer())

#m.layers[3] = state_layer('California')

# Zoom the map

bbox = Box2d(-2607277,-1554066,2391576,1558237)
m.zoom_to_box(bbox)
#m.pan_and_zoom(610, 480, 0.96)
m.zoom(0.96)

# Render to a file

# 'png256' for 8-bit png
render_to_file(m, os.path.join(out_dir, 'usa48.png'), 'png', 1.0) 

bbox_ne = Box2d(230348, -289948,2331777,1276571)
m.zoom_to_box(bbox_ne)

render_to_file(m, os.path.join(out_dir, 'usa48_northeast.png'), 'png', 1.0)

bbox_all = Box2d(-6377775,-2106929,2244702,4808764)
m.zoom_to_box(bbox_all)

render_to_file(m, os.path.join(out_dir, 'usa50.png'), 'png', 1.0)

# Render all states

def render_states(states, prefix, suffix):
    for state in states:
        print("Processing: {0}".format(state))
        m.layers[3] = state_layer(state)
        render_to_file(m, os.path.join(out_dir, '{0}{1}{2}.png'.format(prefix, state, suffix)), 'png', 1.0)
    

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD',
          'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH',
          'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
          'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

m.layers[3:3] = state_layer(states[0])

# Render all states (48 visible)

m.zoom_to_box(bbox)
m.zoom(0.96)
render_states(states, "", "")

# Render northeast states

m.zoom_to_box(bbox_ne)
render_states(['CT', 'DE', 'MA', 'MD', 'NH', 'NJ', 'RI', 'VT'], "ne_", "")

# Render Alaska and Hawaii

m.zoom_to_box(bbox_all)
render_states(['AK', 'HI'], "all_", "")

print("done")
