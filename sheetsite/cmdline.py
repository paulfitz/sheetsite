#!/usr/bin/python

import argparse
import json
import os
from sheetsite.site import Site
from sheetsite.source import read_source
from sheetsite.chain import apply_chain
import sys

def run(argv, param_tweaker=None):
    parser = argparse.ArgumentParser(description='Run a website from a spreadsheet. '
                                     'Take a spreadsheet (from google sheets or locally), and '
                                     'convert it to a .json file that a static website '
                                     'generator like jekyll can use.  Optionally strip private '
                                     'information and add derived geographic fields like '
                                     'latitude and longitude.')

    parser.add_argument('--config', nargs=1, required=False, default=['_sheetsite.json'],
                        help='name of default configuration file.')

    parser.add_argument('--cache-dir', nargs=1, required=False, default=['_cache'],
                        help='name of default cache directory.')

    args = parser.parse_args(argv)

    config_file = args.config[0]
    with open(config_file, 'r') as config:
        params = json.load(config)
    if param_tweaker is not None:
        param_tweaker(params)

    apply_chain(params, args.cache_dir[0])
