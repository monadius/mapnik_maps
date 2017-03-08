import os
from mapnik import *

base_dir = '/Users/monad/Work/data'
cult50m_dir = os.path.join(base_dir, '50m_cultural')
phys50m_dir = os.path.join(base_dir, '50m_physical')

proj4_usa = '+proj=lcc +lat_1=33 +lat_2=45 +lat_0=39 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'

m = Map(1200, 900, proj4_usa)
m.background = Color('#b3e2ee')


# Land

def land_style():
    s = Style()
    r = Rule()

    ps = PolygonSymbolizer()
    ps.fill = Color('#f1daa0')
    r.symbols.append(ps)

    name = 'Land Style'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def land_layer():
    ds = Shapefile(file=os.path.join(phys50m_dir, 'ne_50m_land.shp'))
    layer = Layer('Land')
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

    name = 'USA Style'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def usa_layer():
    ds = Shapefile(file=os.path.join(cult50m_dir, 'ne_50m_admin_0_countries.shp'))
    layer = Layer('USA')
    layer.datasource = ds
    layer.styles.append(usa_style())
    return layer


# Land boundaries

def land_boundaries_style():
    s = Style()
    r = Rule()

    stk = Stroke(Color('#4fadc2'), 1.0)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    name = 'Land Boundaries Style'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def land_boundaries_layer():
    ds = Shapefile(file=os.path.join(phys50m_dir, 'ne_50m_land.shp'))
    layer = Layer('Land Boundaries')
    layer.datasource = ds
    layer.styles.append(land_boundaries_style())
    return layer


# State boundaries

def states_style():
    s = Style()
    r = Rule()

    r.filter = Expression("[adm0_name] = 'United States of America'")

    stk = Stroke(Color('black'), 0.5)
    ls = LineSymbolizer(stk)
    r.symbols.append(ls)

    name = 'States Style'
    s.rules.append(r)
    m.append_style(name, s)
    return name

def states_layer():
    ds = Shapefile(file=os.path.join(cult50m_dir, 'ne_50m_admin_1_states_provinces_lines.shp'))
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
    ds = Shapefile(file=os.path.join(phys50m_dir, 'ne_50m_lakes.shp'))
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
    ds = Shapefile(file=os.path.join(cult50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp'))
    layer = Layer('Admin 0 Boundaries')
    layer.datasource = ds
    layer.styles.append(admin_0_boundaries_style())
    return layer

# Create and add all layers

m.layers.append(land_layer())
m.layers.append(usa_layer())
m.layers.append(land_boundaries_layer())
m.layers.append(states_layer())
m.layers.append(lakes_layer())
m.layers.append(admin_0_boundaries_layer())


# Zoom the map

#bbox = Envelope(Coord(-3977504, -2117694), Coord(5506722, 5492699))
#bbox = Box2d(-2532669,-1898222,2316968,1902394)
bbox = Box2d(-2607277,-1554066,2391576,1558237)
#bbox = mapnik.Envelope(mapnik.Coord(-3977504, -2117694), mapnik.Coord(5500000, 5492699))
#m.zoom_all()
m.zoom_to_box(bbox)
m.zoom(0.96)

# Render to a file

render_to_file(m, 'usa48.png', 'png', 1.0) # 'png256' for 8-bit png
print("done")
