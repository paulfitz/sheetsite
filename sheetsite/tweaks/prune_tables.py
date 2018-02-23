'''

Little Bobby Drop Tables

tweaks:
  prune_tables:
    - Table1  # list of all tables in desired order
    - Table2

'''

def apply(wb, params):
    old_names = wb['names']
    old_tables = wb['tables']
    names = wb['names'] = list(params)
    tables = wb['tables'] = {}
    for name in names:
        tables[name] = old_tables[name]
