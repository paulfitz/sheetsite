#!/usr/bin/python

import argparse
import os
from sheetsite.chain import apply_chain, compute_diff
from sheetsite.expand import load_config
import sys


def run(argv):
    parser = argparse.ArgumentParser(description='Run a website from a spreadsheet. '
                                     'Take a spreadsheet (from google sheets or locally), and '
                                     'convert it to a .json file that a static website '
                                     'generator like jekyll can use.  Optionally strip private '
                                     'information and add derived geographic fields like '
                                     'latitude and longitude.')

    parser.add_argument('--config', nargs='*', required=False,
                        default=['_sheetsite.yml', '_sheetsite.json'],
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
    params = load_config(config_file)
    files = apply_chain(params, args.cache_dir[0])
    diff = compute_diff(files, 'ansi')
    print(diff)


def cmd_sheetsite():
    run(sys.argv[1:])


if __name__ == '__main__':
    cmd_sheetsite()

