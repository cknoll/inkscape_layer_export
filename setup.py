# -*- coding: utf-8 -*-

import os
from setuptools import setup


packagename = "inkscape_layer_export"

# consider the path of `setup.py` as root directory:
PROJECTROOT = os.path.dirname(sys.argv[0]) or "."
__version__ = (
    open(os.path.join(PROJECTROOT, packagename, "release.py"), encoding="utf8")
    .read()
    .split('__version__ = "', 1)[1]
    .split('"', 1)[0]
)

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

setup(
    name=packagename,
    version=__version__,
    author='Carsten Knoll',
    packages=[packagename],
    package_data={'imagedirpreview': ['templates/*']},
    url='https://github.com/cknoll/imagedirpreview',
    license='GPLv3',
    description='Script for generating multiple pdfs from an svg-file according to special layer names',
    long_description="""
    Script for generating multiple pdfs from an svg-file according to special layer names like (containing frame numbers)
    """,
    keywords='svg, pdf, animation, helper script',
    install_requires=requirements,
    entry_points={'console_scripts': ['{0}={0}:main'.format(packagename)]}
)
