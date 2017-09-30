
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
                if code == "CT":
                    row[column] = "Connecticut"
                    # important to replace this or geocoder will sporadically
                    # interpret it as Court or Crescent or the like

    if not active:
        raise KeyError(column)
        
