import os
import sys
sys.path.extend([os.path.abspath("."), os.path.abspath("..")])
from mapnik_xml import *

base_dir = '/Users/monad/Work/data'
cult50m_dir = os.path.join(base_dir, '50m_cultural')
phys50m_dir = os.path.join(base_dir, '50m_physical')
edited50m_dir = os.path.join(base_dir, 'edited50m')

land_file_50m = os.path.join(phys50m_dir, 'ne_50m_land.shp')
land_boundaries_file_50m = os.path.join(phys50m_dir, 'ne_50m_coastline.shp')
boundaries_file_50m = os.path.join(edited50m_dir, 'ne_50m_admin_0_boundary_lines_land.shp')
countries_file_50m = os.path.join(cult50m_dir, 'ne_50m_admin_0_countries.shp')
lakes_file_50m = os.path.join(phys50m_dir, 'ne_50m_lakes.shp')

m = Map(1000, 900, "+proj=longlat +datum=WGS84 +no_defs", [-27, -38, 60, 42])
m.background = "#b3e2ee"

style = Style("land style")
style.symbols.append(PolygonSymbolizer("#f1daa0"))

line = LineSymbolizer("black", 1)
line.add_dash(8, 4)
line.add_dash(2, 2).add_dash(2, 2)
style.symbols.append(line)

land = Layer("land", countries_file_50m)
land.styles.append(style)

style = Style("marker")
style.filter = "[name]='Egypt'"
marker = MarkersSymbolizer("tiny.svg")
marker.scale = (2,1)
marker.translation = (100,-10)
marker.rotation = 80
marker.opacity = 0.5
style.symbols.append(marker)
land.styles.append(style)


m.layers.append(land)
#m.write_xml("a.xml")

if len(sys.argv) > 1:
    render_map(m, "a.png", debug=True)
    # import mapnik
    # m = mapnik.Map(1000, 900)
    # mapnik.load_map(m, "a.xml")
    # m.zoom_to_box(mapnik.Box2d(-27,-38,60,42))
    # mapnik.render_to_file(m, "a.png")