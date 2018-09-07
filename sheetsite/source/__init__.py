import os
from sheetsite.source.csv import read_source_csv
from sheetsite.source.google import read_source_google
from sheetsite.source.excel import read_source_excel
from sheetsite.source.json import read_source_json


def read_source(params):

    readers = {
        '.csv': read_source_csv,
        'google-sheets': read_source_google,
        '.json': read_source_json,
        '.xls': read_source_excel,
        '.xlsx': read_source_excel
    }

    name = None
    if 'name' in params:
        name = params['name']
    elif 'filename' in params:
        _, ext = os.path.splitext(params['filename'])
        name = ext

    if name is None:
        raise IOError('source not specified')

    if name not in readers:
        raise IOError('source not recognized: {}'.format(name))

    return readers[name](params)


