#!/bin/bash




inkscape_layer_export example.svg



for pdfile in example-*.pdf ; do
  convert -verbose -density 500 -resize '600' "${pdfile}" "${pdfile%.*}".png
done

convert -delay 100 -loop 0 *.png example_animation.gif

