import os
import subprocess
from sheetsite.destination.drop import write_destination_drop
from sheetsite.destination.excel import write_destination_excel
from sheetsite.destination.ftp import write_destination_ftp
from sheetsite.destination.git import write_destination_git
from sheetsite.destination.json_ss import write_destination_json
from sheetsite.destination.stone_soup import write_destination_stone_soup

def write_destination_chain(params, state):
    writers = params['chain']
    for writer in writers:
        writer['parent'] = params
        write_destination(writer, state)

def write_destination(params, state):

    writers = {
        'git': write_destination_git,
        'ftp': write_destination_ftp,
        'stone-soup': write_destination_stone_soup,
        'drop': write_destination_drop,
        'chain': write_destination_chain,
        '.xlsx': write_destination_excel,
        '.xls': write_destination_excel,
        '.json': write_destination_json
    }

    name = None
    if 'name' in params:
        name = params['name']
    elif 'output_file' in params:
        _, ext = os.path.splitext(params['output_file'])
        name = ext

    if name not in writers:
        raise IOError('destination not recognized: {}'.format(name))

    return writers[name](params, state)
