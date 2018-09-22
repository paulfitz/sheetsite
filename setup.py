#!/usr/bin/env python

import os
from distutils.core import setup
from setuptools import find_packages
import os.path


def read(fname, fname2):
    if not(os.path.exists(fname)):
        fname = fname2
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="sheetsite",
    version="0.2.2",
    author="Paul Fitzpatrick",
    author_email="paul.michael.fitzpatrick@gmail.com",
    description=("read google sheets, use them for sites"),
    license="MIT",
    keywords="google sheet xls json",
    url="https://github.com/paulfitz/sheetsite",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "sheetsite=sheetsite.cmdline:cmd_sheetsite",
            "sheetwatch=sheetsite.sheetwatch:run"
        ]
    },
    long_description=read('README', 'README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        "daff",
        "dataset>=1.0.2",
        "oauth2client>=2.0.0",
        "openpyxl",
        "pygsheets",
        "pyyaml",
        "requests",
        "six",
        "tqdm"
    ],
    extras_require={
        "queue": [
            "celery",
            "jinja2",
            "premailer",
            "redis"
        ]
    }
)
