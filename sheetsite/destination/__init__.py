import os
import subprocess
from sheetsite.destination.drop import write_destination_drop
from sheetsite.destination.ftp import write_destination_ftp
from sheetsite.destination.git import write_destination_git
from sheetsite.destination.stone_soup import write_destination_stone_soup

def write_destination(params, state):

    writers = {
        'git': write_destination_git,
        'ftp': write_destination_ftp,
        'stone-soup': write_destination_stone_soup,
        'drop': write_destination_drop
    }

    if 'name' not in params:
        return IOError('destination not specified')

    name = params['name']

    if name not in writers:
        return IOError('destination not recognized: {}'.format(name))

    return writers[name](params, state)
