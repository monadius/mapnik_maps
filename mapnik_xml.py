import sys
import os
import xml.etree.ElementTree as ET

def set_attrib(element, name, attrib):
    if attrib:
        element.set(name, str(attrib))

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Map:
    def __init__(self, width, height, proj, bbox):
        self.proj = proj
        self.width = width
        self.height = height
        self.bbox = bbox
        self.background = None
        self.layers = []

    def write_xml(self, fname):
        import xml.dom.minidom
        root = self.to_xml()
        with open(fname, "w") as f:
            xml = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml()
            f.write(xml)

    def to_xml(self):
        styles = {}
        for layer in self.layers:
            for style in layer.styles:
                if style.name in styles:
                    if styles[style.name] != style:
                        eprint("Duplicate style name: {} (layer = {})".format(style.name, layer.name))
                    continue
                styles[style.name] = style

        root = ET.Element("Map", srs=self.proj)
        set_attrib(root, "background-color", self.background)
        set_attrib(root, "maximum-extent", ",".join(map(str, self.bbox)))
       
        for style in styles:
            root.append(styles[style].to_xml())

        for layer in self.layers:
            root.append(layer.to_xml())

        return root


class Layer:
    def __init__(self, name, datasource, style=None):
        self.name = name
        self.datasource = datasource
        self.styles = [style] if style else []

    def to_xml(self):
        layer = ET.Element("Layer", name=self.name, srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
        for style in self.styles:
            ET.SubElement(layer, "StyleName").text = style.name
        ds = ET.SubElement(layer, "Datasource")
        ET.SubElement(ds, "Parameter", name="type").text = "shape"
        ET.SubElement(ds, "Parameter", name="file").text = self.datasource
        return layer


class Style:
    def __init__(self, name):
        self.name = name
        self.filter = None
        self.symbols = []

    def to_xml(self):
        style = ET.Element("Style", name=self.name)
        rule = ET.SubElement(style, "Rule")
        if self.filter:
            ET.SubElement(rule, "Filter").text = self.filter
        for sym in self.symbols:
            rule.append(sym.to_xml())
        return style


class LineSymbolizer:
    def __init__(self, stroke, stroke_width):
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.stroke_opacity = None
        self.dashes = []

    def add_dash(self, length, gap):
        self.dashes.append((length, gap))
        return self

    def to_xml(self):
        el = ET.Element("LineSymbolizer")
        set_attrib(el, "stroke", self.stroke)
        set_attrib(el, "stroke-width", self.stroke_width)
        set_attrib(el, "stroke-opacity", self.stroke_opacity)
        set_attrib(el, "stroke-dasharray", " ".join(",".join(map(str, d)) for d in self.dashes))
        return el


class PolygonSymbolizer:
    def __init__(self, fill):
        self.fill = fill
        self.fill_opacity = None

    def to_xml(self):
        el = ET.Element("PolygonSymbolizer")
        set_attrib(el, "fill", self.fill)
        set_attrib(el, "fill-opacity", self.fill_opacity)
        return el


class MarkersSymbolizer:
    def __init__(self, file):
        self.file = os.path.abspath(file)
        self.opacity = 1.0
        self.scale = None
        self.translation = None
        self.rotation = None
        self.allow_overlap = None

    def to_xml(self):
        el = ET.Element("MarkersSymbolizer")
        el.set("file", self.file)
        set_attrib(el, "opacity", self.opacity)
        set_attrib(el, "allow-overlap", self.allow_overlap)
        transforms = []
        if self.translation:
            transforms.append("translate({})".format(",".join(map(str, self.translation))))
        if self.rotation:
            transforms.append("rotate({})".format(self.rotation))
        if self.scale:
            scale = (self.scale,) if isinstance(self.scale, (int, long, float)) else self.scale
            transforms.append("scale({})".format(",".join(map(str, scale))))
        set_attrib(el, "transform", " ".join(transforms))
        return el


def render_map(map_obj, out_fname, out_format='png', scale=1.0, debug=False):
    import mapnik
    if debug:
        map_obj.write_xml("a.xml")
    m = mapnik.Map(map_obj.width, map_obj.height, map_obj.proj)
    mapnik.load_map_from_string(m, ET.tostring(map_obj.to_xml()))
    m.zoom_all()
    mapnik.render_to_file(m, out_fname, out_format, scale)

