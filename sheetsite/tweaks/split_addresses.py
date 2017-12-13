
'''

Addresses separated by newlines in a single cell get parsed

tweaks:
  split_addresses:
    column: "Other Addresses"

'''


import re


def sanity_stick(locs):
    if len(locs) <= 1:
        return locs
    if len(re.sub(r'[^,]', '', locs[0])) < 3:
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
                if cell is not None:
                    print("[{}]".format(cell))
                    cell = re.sub(r'^[ \n\r\t]*', '', cell)
                    cell = re.sub(r'[ \n\r\t]*$', '', cell)
                    cell = re.sub(r'^n/a$', '', cell, flags=re.IGNORECASE)
                    print("[{}]".format(cell))
                    if cell == '':
                        splits = None
                    else:
                        splits = cell.split('\n')
                        splits = sanity_stick(splits)
                    row[column] = splits
    if not active:
        raise KeyError(column)
        
    
