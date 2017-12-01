
def apply(wb, params):
    column = params['column']
    table = params.get('table')
    mapping = params['map']
    active = False
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if column not in t['columns']:
                continue
            active = True
            for row in t['rows']:
                code = str(row[column])
                if "," in code:
                    cactive = False
                    codes = [x.strip() for x in code.split(',')]
                    for idx, code in enumerate(codes):
                        if code in mapping:
                            codes[idx] = mapping[code]
                            cactive = True
                    if cactive:
                        code = ', '.join(codes)
                        row[column] = code
                elif code in mapping:
                    row[column] = mapping[code]

    if not active:
        raise KeyError(column)
        
