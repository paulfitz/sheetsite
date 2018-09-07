'''
Replaces all blank values in a column with the first non-blank value in a series
of columns, falling back on a default_value if all are blank.
```
tweaks:
  coalesce:
    # the first of the following list of columns is the one that is modified
    columns: first_priority_column second_priority_column third_priority_column
    default_value: N/A
    table: sheet1    # optional
```
'''

def apply(wb, params):
    columns = params['columns']
    default_value = params['default']
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
                    if v is not None and v != "":
                        break
                    v = row[column]
                if v is None or v == '':
                    v = default_value
                row[columns[0]] = v
    if not active:
        raise KeyError(column)
