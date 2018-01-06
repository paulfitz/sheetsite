
'''

Smush all the tables together.

tweaks:
  merge_tables:
    table: directory   # name of the single created table
    column: thing      # sheet names are placed here

'''

def apply(wb, params):
    table = params['table']
    column = params['column']
    input_names = wb['names']
    input_tables = wb['tables']
    wb['names'] = [table]
    target_table = {}
    wb['tables'] = {
        table: target_table
    }
    order_cols = []
    seen_cols = set()
    tables = [(name, input_tables[name]) for name in input_names]
    for name, t in tables:
        cols = t['columns']
        for col in cols:
            if col not in seen_cols:
                order_cols.append(col)
                seen_cols.add(col)
    if column not in seen_cols:
        order_cols.append(column)
        seen_cols.add(column)
        
    target_table['columns'] = order_cols
    rows = target_table['rows'] = []
    for name, t in tables:
        extra = dict((c, None) for c in seen_cols - set(t['columns']))
        for row in t['rows']:
            row.update(extra)
            row[column] = name
            rows.append(row)
    
