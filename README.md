# inkscape_layer_export

Simple script to export arbitrary combinations of layers of an inkscape document
to separate files. This is useful to create simple animations or sets of graphics
which share significant elements.

![example animation](examples/example_animation.gif "example animation")

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

    arbitrary_layername4__[2,4,5--end]
    short__[2--end]
    another_arbitrary_layername__[1,2,3]
    arbitrary_layername1__[1--end]
    layer0815

*Note*: Layers without square brackets are ignored and not visible in any frame.

**Frame generation**

Open a terminal/konsole in the directory were your target svg-file is located
and type `inkscape_layer_export targetfile.svg`.

This should generate a pdf-file for each frame and (if `pdftk` is installed)
an overview-pdf, containing all frames as single pages.

**Usage of the generated frames**

* create a animated gif linke in `examples/convert.sh`
* use with LaTeX-Beamer:

->

    \begin{textblock*}{\textwidth}[0.,0.](10mm,20mm)
        \setlength{\mywidth}{0.9\textwidth}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-01}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-02}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-03}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-04}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-05}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-06}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-07}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-08}}
        \only<+>{\includegraphics[width=\mywidth]{img-src/example-09}}
    \end{textblock*}


## Furhter plans

The current state of the script suffices to fulfill the needs of the author.
However, it would make sense to convert the script into an inkscape plugin,
add different output options (e.g., gif), make it more robust, etc.
Feel free to open issues and send pull requests.
