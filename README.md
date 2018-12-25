# inkscape_layer_export

Simple script to export arbitrary combinations of layers of an inkscape document
to separate files. This is useful to create simple animations or sets of graphics
which share significant elements.

## Installation

`pip install inkscape_layer_export`

This installs the python package and an executable script.

Optional:

## Usage
**Background**

The script parses the *names of the layers* of your document to determine
how many frames occur and which layer should be visibile in which frames.
Syntax: Frame specification is delimited by `__[` (start) and  `]` (end).
Valid layer names are, e.g.:

    arbitrary_layername4__[2, 4]
    short__[2--end]
    another_arbitrary_layername__[1, 2, 3]
    arbitrary_layername1__[1--end]
    layer0815

*Note*: Layers without square brackets are ignored and not visible in any frame.

**Frame generation**

Open a terminal/konsole in the directory were your target svg-file is located
and type `inkscape_layer export targetfile.svg`.

This should generate a pdf-file for each frame and (if `pdftk` is installed)
an overview-pdf, containing all frames as single pages.


## Furhter plans

The current state of the script suffices to fulfill the needs of the author.
However, it would make sense to convert the script into an inkscape plugin,
add different output options (e.g., gif), make it more robust, etc.
Feel free to open issues and send pull requests.
