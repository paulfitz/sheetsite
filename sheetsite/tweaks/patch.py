'''

Patch a cell

tweaks:
  patch:
    where:
      col1: val1
      col2: val2
    update:
      col3: val3
'''

def apply(wb, params):
    where = params['where']
    update = params['update']
    for name, t in wb['tables'].items():
        for row in t['rows']:
            ok = True
            active = True
            for key, val in where.items():
                if key not in row:
                    ok = False
                    break
                if row[key] != val:
                    active = False
                    break
            if not ok:
                break
            if not active:
                continue
            for key, val in update.items():
                row[key] = val
