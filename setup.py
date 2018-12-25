# -*- coding: utf-8 -*-

from setuptools import setup
from inkscape_layer_export.release import __version__

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

setup(
    name='inkscape_layer_export',
    version=__version__,
    author='Carsten Knoll',
    packages=['inkscape_layer_export'],
    package_data={'imagedirpreview': ['templates/*']},
    url='https://github.com/cknoll/imagedirpreview',
    license='GPLv3',
    description='Script for generating multiple pdfs from an svg-file according to special layer names',
    long_description="""
    Script for generating multiple pdfs from an svg-file according to special layer names like (containing frame numbers)
    """,
    keywords='svg, pdf, animation, helper script',
    install_requires=requirements,
    entry_points={'console_scripts': ['inkscape_layer_export=inkscape_layer_export:main']}
)
