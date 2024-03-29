#!/usr/bin/env python3

"""

https://graphicdesign.stackexchange.com/questions/5880/how-can-you-export-an-inkscape-svg-file-to-a-pdf-and-maintain-the-integrity-of-t

inkscape --file=mySVGinputFile.svg --export-area-drawing --without-gui --export-pdf=output.pdf

"""

from lxml import etree
import os
import sys
import re
import argparse
from ipydex import IPS, activate_ips_on_exception
# activate_ips_on_exception()


# TODO: implement node_name self
from svglib.svglib import node_name

# from ipydex import IPS


IS_PREFIX = "{http://www.inkscape.org/namespaces/inkscape}"


class Container(object):
    pass


class Lazymap(object):
    """
    s = '{foo} {bar}'

    s.format_map(Lazymap(bar="FOO"))
    >>> '{foo} FOO'

    s.format_map(Lazymap(bar="BAR"))
    >>> '{foo} BAR'

    s.format_map(Lazymap(bar="BAR", foo="FOO", baz="BAZ"))
    >>> 'FOO BAR'
    """
    def __init__(self, **kwargs):
        self.dict = kwargs

    def __getitem__(self, key):
        return self.dict.get(key, "".join(["{", key, "}"]))


# global Data Container
C = Container()


C.inkscape_cmd_template = "inkscape --file={in_file} --export-area-page " \
                          "--without-gui --export-ignore-filters {export_format}={out_file} {res_string}"


def run_command(cmd, msg):
    """
    helper function: run command an give a meaningful error message
    """

    returncode = os.system(cmd)
    if returncode == 0:
        print(msg)
    else:
        print("Error (returncode={}). Tried to execute `{}`".format(returncode, cmd))


def islayer(svgnode):
    """
    determine if an xml node of an svg is a layer object
    """
    if not node_name(svgnode) == "g":
        return False
    gmkey = "{}groupmode".format(IS_PREFIX)
    grp_mode = svgnode.attrib.get(gmkey, None)

    if grp_mode == "layer":
        return True

    return False


class Layer(object):
    """
    Inksacpe layer class
    """
    maxframe = None

    def __init__(self, svg_node):
        self.svg_node = svg_node
        self._get_attributes()
        self.frame_id_str = self._get_desired_frames_id_strings()
        self.frames = None

    def __repr__(self):
        return "Layer. label='{}', attrib={}".format(self.label,
                                                     self.svg_node.attrib)

    def _get_attributes(self):
        self.style = self.svg_node.attrib.get("style")
        self.label = self.svg_node.attrib.get("{}label".format(IS_PREFIX))

    def _get_desired_frames_id_strings(self):
        """
        assume, that the frame numbers, where this layer should be visble is
        encoded in the layer-name like one of
         - self.label == "some_string__[1, 2, 4, 7]"
         - self.label == "some_string__[3--6]"
         - self.label == "some_string__[3--end]"
        """

        if not ("__[" in self.label and self.label.endswith("]")):
            # this layer is not desired in the result
            return ""

        # IPS()
        idx = self.label.index("__[") + len("__[")

        frame_id_str = self.label[idx:-1]

        return frame_id_str

    def gen_desired_frames(self):
        """
        generate desired frames (from string expressions like "3--end")

        assume that maxframe has bien set
        """

        assert Layer.maxframe is not None

        frame_id_str = self.frame_id_str.replace("end", "{}".format(Layer.maxframe + 1))

        # now we only have expressions like "3--12" or "1, 2, 3"
        # resolve the first one:
        ranges = re.findall(r'\d+--\d+', frame_id_str)

        self.frames = []

        for r in ranges:
            i1, i2 = map(int, r.split("--"))
            lst = list(range(i1, i2 + 1))
            frame_id_str = frame_id_str.replace(r, "")
            frame_id_str = frame_id_str.replace(", ,", ",")
            frame_id_str = frame_id_str.replace(",,", "")

            self.frames.extend(lst)

        # look for remaining regular sequences (# like 3, 4, 5)
        frame_str_list = frame_id_str.split(",")

        # TODO: catch errors and produce meaningful message
        print(frame_str_list)
        for frame_str in frame_str_list:
            if frame_str == "":
                continue
            try:
                self.frames.append(int(frame_str))
            except ValueError as err:
                # IPS()
                print("int-conversion-error for layer:`{}`".format(self.label))
                raise err

        self.frames.sort()

    def set_visibility(self, visibility_flag):
        """
        modify the `style` attribute of self.svg_node to either
        "...;display:none" -> layer invisible
        or
        "...;display:inline" - layer visible
        other properties (such as opacity) are not changed
        """

        style_str = self.svg_node.attrib.get("style")

        if not style_str:
            style_str = "display:none"

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
        new_style_str = ";".join(["{}:{}".format(k, v) for k, v in style_dict.items()])

        print("{}: {}  -->  {}".format(self.label, style_str, new_style_str))

        # change the actual svg-object
        self.svg_node.attrib["style"] = new_style_str


# noinspection PyUnusedLocal
def read_svg(path, **kwargs):
    """
    Parse svg-Document
    """

    # load SVG file
    parser = etree.XMLParser(remove_comments=True, recover=True)
    try:
        doc = etree.parse(path, parser=parser)
        svg_object = doc.getroot()
    except Exception as exc:
        svg_object = None
        print("Failed to load input file! (%s)" % exc)
        exit()

    return svg_object


def determine_max_frame(layers):

    all_numbers = []

    for lyr in layers:
        all_numbers.extend(re.findall(r'\d+', lyr.frame_id_str))
        print(lyr.label, "all_numbers:", all_numbers)

    all_numbers = list(map(int, all_numbers))
    all_numbers.sort()
    print("all_numbers:", all_numbers, "..->", int(all_numbers[-1]))

    # TODO: handle case of empty list
    return int(all_numbers[-1])


def get_layer_list(svg):
    all_elements_it = svg.getiterator()
    layers = []

    for elt in all_elements_it:
        if islayer(elt):
            lyr = Layer(elt)
            print(lyr.label, ":", lyr.style, lyr.frames)
            layers.append(lyr)

    Layer.maxframe = determine_max_frame(layers)

    for lyr in layers:
        lyr.gen_desired_frames()

    return layers


def render_layer_selections(layer_list, svg_obj, **kwargs):
    """
    For each frame interate through layer_list,
    and set the visibility accordingly
    """

    # the path is needed by the used library to determine the directory
    # this might be the place to inject a specific outdir
    svgpath = svg_obj.base

    filetype = kwargs.get("filetype")

    # TODO: maybe support other endings.. (e.g. "svg")
    assert svgpath.endswith(".svg")
    svgbasename = os.path.basename(svgpath)
    svgdir = os.path.dirname(svgpath)

    tmpsvgpath = None

    # iterate over frames (starting with 1, including maxframe)
    for framenbr in range(1, Layer.maxframe + 1):
        print("\n\n-- Frame: {}\n".format(framenbr))
        # visible_layers = []
        # invisible_layers = []

        outf_basename = kwargs.get("outputbasename")
        if not outf_basename:
            outf_basename = svgbasename.replace(".svg", "-{:02d}.{}".format(framenbr, filetype))

        targetpath = os.path.join(svgdir, outf_basename)

        for layer in layer_list:
            # check if current framenbr is desired for this layer
            if framenbr in layer.frames:
                layer.set_visibility(1)
            else:
                layer.set_visibility(0)

        tmpsvgpath = "__tmp__.svg"
        with open(tmpsvgpath, "w") as svgfile:
            svgfile.write(etree.tostring(svg_obj, encoding="utf8", pretty_print=True).decode("utf8"))

        cmd = C.inkscape_cmd_template.format(in_file=tmpsvgpath, out_file=targetpath)
        run_command(cmd, msg="{} written".format(targetpath))

        # TODO: delete tmpsvgpath

    if tmpsvgpath:
        os.remove(tmpsvgpath)

    if filetype == "pdf":
        pdfwildcardpath = svgbasename.replace(".svg", "-*.pdf")
        pdfallpath = svgbasename.replace(".svg", "_all.pdf")
        pdftkcommand = "pdftk {} cat output {}".format(pdfwildcardpath, pdfallpath)

        run_command(pdftkcommand, "overview generated")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="the svg file which should be processed")
    parser.add_argument("-f", "--filetype", help="choose between pdf (default) and png", choices=["pdf", "png"], default="pdf")
    parser.add_argument("-o", "--outputbasename", help="first part of name of output file", default=None)
    parser.add_argument("-r", "--resolution", help="resolution (dpi) for png output", default=100)

    args = parser.parse_args()

    if args.filetype == "png":
        res_string = "--export-dpi={}".format(args.resolution)
    else:
        res_string = ""

    export_formats = dict(pdf="--export-pdf", svg="--export-plain-svg", png="--export-png")

    valid_file_types = list(export_formats.keys())
    if args.filetype not in valid_file_types:
        msg = "invalid filetype (must be one of {})".format(valid_file_types)
        raise ValueError(msg)


    svg = read_svg(args.inputfile)
    ll = get_layer_list(svg)

    # noinspection PyTypeChecker
    C.inkscape_cmd_template = \
        C.inkscape_cmd_template.format_map(Lazymap(export_format=export_formats[args.filetype], res_string=res_string))

    # IPS()
    render_layer_selections(ll, svg, filetype=args.filetype, outputbasename=args.outputbasename)



