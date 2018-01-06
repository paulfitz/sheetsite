
def apply(wb, params):
    column = params['column']
    table = params.get('table')
    value = params.get('value')
    not_value = params.get('not-value')
    active = False
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if column not in t['columns']:
                continue
            active = True
            orows = []
            for row in t['rows']:
                v = row[column]
                if value is not None:
                    if v == value:
                        orows.append(row)
                elif not_value is not None:
                    if v != not_value:
                        orows.append(row)
                elif v is not None and v != '':
                    orows.append(row)
            t['rows'] = orows
    if not active:
        raise KeyError(column)
        
