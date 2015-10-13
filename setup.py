#!/usr/bin/env python

import os
from distutils.core import setup
from distutils.command.build_py import build_py
from subprocess import call
import json
import os.path

class my_build_py(build_py):
    def run(self):
        # actually I have nothing special to do yet
        build_py.run(self)

def read(fname, fname2):
    if not(os.path.exists(fname)):
        fname = fname2
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name = "sheetsite",
    version = "0.1.6",
    author = "Paul Fitzpatrick",
    author_email = "paul.michael.fitzpatrick@gmail.com",
    description = ("read google sheets, use them for sites"),
    license = "MIT",
    keywords = "google sheet xls json",
    url = "https://github.com/paulfitz/sheetsite",
    packages=['sheetsite'],
    scripts=['bin/sheetsite'],
    long_description=read('README', 'README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        "gspread",
        "oauth2client",
        "xlwt"
    ],
    cmdclass={'build_py': my_build_py}
)
