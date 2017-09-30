
def apply(wb, params):
    column = params['column']
    table = params.get('table')
    active = False
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if column not in t['columns']:
                continue
            active = True
            orows = []
            for row in t['rows']:
                v = row[column]
                if v is not None and v != "":
                    orows.append(row)
            t['rows'] = orows
    if not active:
        raise KeyError(column)
        
