#!/usr/bin/env python3

"""

https://graphicdesign.stackexchange.com/questions/5880/how-can-you-export-an-inkscape-svg-file-to-a-pdf-and-maintain-the-integrity-of-t

inkscape --file=mySVGinputFile.svg --export-area-drawing --without-gui --export-pdf=output.pdf





"""


from svglib.svglib import node_name, SvgRenderer
import svglib
from lxml import etree
import os
import sys

from ipydex import IPS


IS_PREFIX="{http://www.inkscape.org/namespaces/inkscape}"

# source: https://graphicdesign.stackexchange.com/questions/5880/how-can-you-export-an-inkscape-svg-file-to-a-pdf-and-maintain-the-integrity-of-t
inkscape_cmd_template = "inkscape --file={} --export-area-page --without-gui --export-pdf={}"


def run_command(cmd, msg):

    returncode = os.system(cmd)
    if returncode == 0:
        print(msg)
    else:
        print("Error (returncode={}). Tried to execute `{}`".format(returncode, cmd))


def islayer(svgnode):
    if not node_name(svgnode) == "g":
        return False
    gmkey = "{}groupmode".format(IS_PREFIX)
    gm = svgnode.attrib.get(gmkey, None)

    if gm == "layer":
        return True

    return False

class Layer(object):
    maxframe = None

    def __init__(self, svg_node):
        self.svg_node = svg_node
        self._get_attributes()
        self.frames = self._get_desired_frames()

    def __repr__(self):
        return "Layer. label='{}', attrib={}".format(self.label,
                                                     self.svg_node.attrib)

    def _get_attributes(self):
        self.style = self.svg_node.attrib.get("style")
        self.label = self.svg_node.attrib.get("{}label".format(IS_PREFIX))

    def _get_desired_frames(self):
        """
        assume the frame_number, where this layer should occour is encoded in the
        layer-name like self.label == "some_string__[1, 2, 4, 7]"
        """

        if not ( "__[" in self.label and self.label.endswith("]") ):
            # this layer is not desired in the result
            return []

        #IPS()
        idx = self.label.index("__[") + len("__[")

        frame_str_list = self.label[idx:-1].split(",")

        # todo: catch errors and produce meaningful message
        frame_list = list(map(int, frame_str_list))

        if frame_list == []:
            return []

        mf = max(frame_list)
        if Layer.maxframe is None or mf > Layer.maxframe:
            Layer.maxframe = mf

        return frame_list

    def set_visibility(self, visibility_flag):
        """
        modify the `style` attribute of self.svg_node to either
        "...;display:none" -> layer invisible
        or
        "...;display:inline" - layer visible
        other properties (such as opacity) are not changed
        """

        style_str = self.svg_node.attrib.get("style")
        # assume this is a ";"-separated list of ":"-separated key-value-pairs

        items = []
        for pair in style_str.split(";"):
            k, v = pair.split(":")
            items.append((k, v))
        style_dict = dict(items)

        if visibility_flag:
            style_dict["display"] = "inline"
        else:
            style_dict["display"] = "none"

        # now convert back to string representation
        new_style_str = ";".join(["{}:{}".format(k,v) for k,v in style_dict.items()])

        print("{}: {}  -->  {}".format(self.label, style_str, new_style_str))

        # change the actual svg-object
        self.svg_node.attrib["style"]=new_style_str





def read_svg(path, **kwargs):
    "Convert an SVG file to an RLG Drawing object."

    # unzip .svgz file into .svg
    unzipped = False
    if isinstance(path, str) and os.path.splitext(path)[1].lower() == ".svgz":
        data = gzip.GzipFile(path, "rb").read()
        open(path[:-1], 'w').write(data)
        path = path[:-1]
        unzipped = True

    # load SVG file
    parser = etree.XMLParser(remove_comments=True, recover=True)
    try:
        doc = etree.parse(path, parser=parser)
        svg = doc.getroot()
    except Exception as exc:
        logger.error("Failed to load input file! (%s)" % exc)
        exit()

    return svg

def layer_list(svg):
    all_elements_it = svg.getiterator()
    layers = []

    for elt in all_elements_it:
        if islayer(elt):
            lyr = Layer(elt)
            print(lyr.label,":", lyr.style, lyr.frames)
            layers.append(lyr)

    return layers


def render_layer_selections(layer_list, **kwargs):
    """
    For each frame interate through layer_list,
    and set the visibility accordingly
    """

    # the path is needed by the used library to determine the directory
    # this might be the place to inject a specific outdir
    svgpath = svg.base

    # TODO: maybe support other endings.. (e.g. "svg")
    assert svgpath.endswith(".svg")
    svgbasename = os.path.basename(svgpath)
    svgdir = os.path.dirname(svgpath)

    # iterate over frames (starting with 1, including maxframe)
    for framenbr in range(1, Layer.maxframe + 1):
        print("\n\n-- Frame: {}\n".format(framenbr))
        visible_layers = []
        invisible_layers = []


        pdfbasename = svgbasename.replace(".svg", "-{:02d}.pdf".format(framenbr))

        targetpath = os.path.join(svgdir, pdfbasename)

        for layer in layer_list:
            # check if current framenbr is desired for this layer
            if framenbr in layer.frames:
                layer.set_visibility(1)
            else:
                layer.set_visibility(0)


        tmpsvgpath = "__tmp__.svg"
        with open(tmpsvgpath, "w") as svgfile:
            svgfile.write(etree.tostring(svg, encoding="utf8", pretty_print=True).decode("utf8"))

        #IPS()
        #exit()

        cmd = inkscape_cmd_template.format(tmpsvgpath, targetpath)
        result = os.system(cmd)
        run_command(cmd, msg="{} written".format(targetpath))

        # TODO: delete tmpsvgpath


    pdfwildcardpath = svgbasename.replace(".svg", "*.pdf")
    pdfallpath = svgbasename.replace(".svg", "-all.pdf")
    pdftkcommand = "pdftk {} cat output {}".format(pdfwildcardpath, pdfallpath)

    run_command(pdftkcommand, "overview generated")




svg = read_svg(sys.argv[1])
ll = layer_list(svg)
render_layer_selections(ll)
