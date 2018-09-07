'''

Rename a table

tweaks:
  rename_table:
    from: OldName
    to: NewName

'''

def apply(wb, params):
    from_name = params['from']
    to_name = params['to']
    old_names = wb['names']
    if from_name in old_names:
        wb['names'] = [to_name if name == from_name else name for name in old_names]
        wb['tables'][to_name] = wb['tables'].pop(from_name)
