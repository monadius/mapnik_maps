import sys
import mapnik

stylesheet = "test.xml"
if len(sys.argv) > 1:
    stylesheet = sys.argv[1]

image = "test.png"
m = mapnik.Map(800, 600)
mapnik.load_map(m, stylesheet)
m.zoom_all()
mapnik.render_to_file(m, image)
print("rendered image to {}".format(image))