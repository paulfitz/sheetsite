'''
Early add id - this stuff needs to get reworked

(stone soup only)
'''

import json

def apply3(wb, params, state):
    column = params['column']
    id_file = state['id_file']
    ids = json.load(open(id_file, 'r'))
    for name, t in wb['tables'].items():
        if name in ids:
            ids0 = ids[name]
            if column not in t['columns']:
                t['columns'].append(column)
            for i, row in enumerate(t['rows']):
                idx = str(i + 1)
                row[column] = ids0[idx]
