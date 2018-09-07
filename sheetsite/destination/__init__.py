import os
import subprocess
from sheetsite.destination.drop import write_destination_drop
from sheetsite.destination.excel import write_destination_excel
from sheetsite.destination.ftp import write_destination_ftp
from sheetsite.destination.git import write_destination_git
from sheetsite.destination.json_ss import write_destination_json
from sheetsite.destination.stone_soup import write_destination_stone_soup
from sheetsite.destination.sqlite_ss import write_destination_sqlite
from sheetsite.destination.csv_ss import write_destination_csv

def write_destination_chain(params, state):
    writers = params['chain']
    for writer in writers:
        writer['parent'] = params
        write_destination(writer, state)

def write_destination(params, state):

    if isinstance(params, list):
        params = {
            'name': 'chain',
            'chain': params
        }

    writers = {
        'chain': write_destination_chain,
        'drop': write_destination_drop,
        'ftp': write_destination_ftp,
        'git': write_destination_git,
        'stone-soup': write_destination_stone_soup,
        '.sqlite': write_destination_sqlite,
        '.sqlite3': write_destination_sqlite,
        '.json': write_destination_json,
        '.xlsx': write_destination_excel,
        '.xls': write_destination_excel,
        '.csv': write_destination_csv,
        'drop': write_destination_drop,
        'chain': write_destination_chain
    }

    name = None
    if 'name' in params:
        name = params['name']
    elif 'step' in params and params['step'] != 'save':
        name = params['step']
    elif 'output_file' in params:
        _, ext = os.path.splitext(params['output_file'])
        name = ext
    elif 'file' in params:
        _, ext = os.path.splitext(params['file'])
        name = ext
        params['output_file'] = params['file']

    if name not in writers:
        import importlib
        return importlib.import_module('sheetsite.destination.{}'.format(name)).apply(params,
                                                                                      state)

    return writers[name](params, state)
