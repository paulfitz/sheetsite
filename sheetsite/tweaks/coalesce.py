def apply(wb, params):
    columns = params['columns']
    table = params.get('table')
    active = False
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if len(set(columns) - set(t['columns'])) > 0:
                continue
            active = True
            for row in t['rows']:
                v = None
                for column in columns:
                    if v is not None:
                        break
                    v = row[column]
                row[columns[0]] = v
    if not active:
        raise KeyError(column)
