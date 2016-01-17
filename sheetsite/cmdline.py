#!/usr/bin/python

import argparse
import json
import os
from sheetsite.chain import apply_chain, compute_diff
from sheetsite.expand import expand
from sheetsite.site import Site
from sheetsite.source import read_source
import sys

def expand_all(o):
    if type(o) == dict:
        return dict([[k, expand_all(v)] for k, v in o.items()])
    if type(o) == list:
        return [expand_all(x) for x in o]
    if type(o) == str or type(o) == unicode:
        return expand(o)
    return o

def run(argv):
    parser = argparse.ArgumentParser(description='Run a website from a spreadsheet. '
                                     'Take a spreadsheet (from google sheets or locally), and '
                                     'convert it to a .json file that a static website '
                                     'generator like jekyll can use.  Optionally strip private '
                                     'information and add derived geographic fields like '
                                     'latitude and longitude.')

    parser.add_argument('--config', nargs='*', required=False, default=['_sheetsitex.json', '_sheetsite.yml'],
                        help='name of configuration file.')

    parser.add_argument('--cache-dir', nargs=1, required=False, default=['_cache'],
                        help='name of default cache directory.')

    args = parser.parse_args(argv)

    config_file = None
    for config_candidate in args.config:
        if os.path.exists(config_candidate):
            config_file = config_candidate
            break
    if not config_file:
        print("Could not find config file", args.config)
        exit(1)
    with open(config_file, 'r') as config:
        _, ext = os.path.splitext(config_file)
        ext = ext.lower()
        if ext == '.yml' or ext == '.yaml':
            import yaml
            params = yaml.safe_load(config)
        else:
            params = json.load(config)
        params = expand_all(params)  # should make this optional

    files = apply_chain(params, args.cache_dir[0])
    diff = compute_diff(files, 'ansi')
    print(diff)
