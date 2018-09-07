'''

Rename a column

tweaks:
  rename_column:
    table: Table1  # optional
    from: OldColumnName
    to: NewColumnName # blank to delete

'''

def apply(wb, params):
    table = params.get('table')
    from_name = params['from']
    to_name = params.get('to')
    active = False
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if from_name not in t['columns']:
                continue
            active = True
            t['columns'] = [to_name if name == from_name else name
                            for name in t['columns']
                            if name != from_name or to_name]
            for row in t['rows']:
                tmp = row[from_name]
                if to_name:
                    row[to_name] = tmp
    if not active:
        raise KeyError(from_name)

