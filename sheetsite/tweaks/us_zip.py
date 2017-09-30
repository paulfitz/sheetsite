
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
                code = str(row[column])
                if len(code) < 5 and len(code) > 0:
                    try:
                        code = "%05d" % int(code)
                        row[column] = code
                    except ValueError:
                        pass  # let odd values through
    if not active:
        raise KeyError(column)
        
