def apply(wb, params):
    formula = params['formula']
    column = params['column']
    table = params.get('table')
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if column not in t['columns']:
                t['columns'].append(column)
            for row in t['rows']:
                row[column] = formula.format(**row)
