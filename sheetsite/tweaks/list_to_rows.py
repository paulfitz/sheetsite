
'''

Take a list and make extra rows from it

tweaks:
  list_to_rows:
    column: "Other Addresses"
    target: "address"  # optional

'''


import copy
import re
import six


def apply(wb, params):
    column = params['column']
    target = params.get('target', column)
    table = params.get('table')
    active = False
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if column not in t['columns']:
                continue
            if target not in t['columns']:
                continue
            active = True
            orows = []
            for row in t['rows']:
                cell = row[column]
                print(">>>>", cell)
                orows.append(row)
                if cell is not None:
                    if not isinstance(cell, six.string_types):
                        for part in cell:
                            nrow = copy.deepcopy(row)
                            nrow[column] = None
                            nrow[target] = part
                            orows.append(nrow)
            t['rows'] = orows
    if not active:
        raise KeyError(column + " / " + target)
        
    
