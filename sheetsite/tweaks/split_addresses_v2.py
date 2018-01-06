
'''

Addresses separated by *double* newlines in a single cell get parsed

tweaks:
  split_addresses_v2:
    column: "Other Addresses"

'''


import json
import re


def sanity_stick(locs):
    if len(locs) <= 1:
        return locs
    if len(re.sub(r'[^,]', '', locs[0])) < 1:
        return [' '.join(locs)]
    return locs


def apply(wb, params):
    column = params['column']
    table = params.get('table')
    active = False
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if column not in t['columns']:
                continue
            active = True
            for row in t['rows']:
                cell = row[column]
                if cell is not None and 'See:' in cell:
                    cell = None
                if cell is not None:
                    print(">>> {}".format(cell))
                    cell = re.sub(r'^[ \n\r\t]*', '', cell)
                    cell = re.sub(r'[ \n\r\t]*$', '', cell)
                    cell = re.sub(r'^n/a$', '', cell, flags=re.IGNORECASE)
                    if cell == '':
                        splits = None
                    else:
                        splits = re.split('[\n\r][\n\r]', cell)
                        splits = sanity_stick(splits)
                    print(json.dumps(splits))
                    row[column] = splits
    if not active:
        raise KeyError(column)
        
    
