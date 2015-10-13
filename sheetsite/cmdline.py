#!/usr/bin/python

import argparse
import os
import sys
from sheetsite.spreadsheet import Spreadsheet

def run():
    parser = argparse.ArgumentParser(description='Fetch a google spreadsheet.')
    parser.add_argument('--credential', nargs=1, required=True, help='credential json file '
                        'from google, see http://gspread.readthedocs.org/en/latest/oauth2.html '
                        '(and don\'t forget to share the spreadsheet with client_email)')
    parser.add_argument('spreadsheet_key', help='key for spreadsheet (e.g. 2LvBgFe...F2qAIuBk)')
    parser.add_argument('output_file', help='file to write to, either output.xls or output.json. '
                        'When saving to xls, the file will not retain original formatting. '
                        'When saving to json, the first row is assumed to contain column names.')

    args = parser.parse_args()

    ss = Spreadsheet()
    ss.connect(args.credential[0])
    ss.load_remote(args.spreadsheet_key)
    ss.save_local(args.output_file)
