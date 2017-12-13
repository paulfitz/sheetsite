
def apply(wb, params):
    table = params.get('table')
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if 'dcc_status' not in t['columns']:
                t['columns'].append('dcc_status')
            if 'dcc_stamp' not in t['columns']:
                t['columns'].append('dcc_stamp')
            for row in t['rows']:
                status = None
                stamp = None
                if 'NOTES' in t['columns']:
                    code = str(row['NOTES'] or '')
                    if 'DELETE' in code:
                        status = 'Inactive'
                if 'Active' in t['columns']:
                    code = str(row['Active'] or '')
                    if code == 'no':
                        status = 'Inactive'
                    elif len(code) > 0 and code[0] >= '0' and code[0] <= '9':
                        stamp = int(code)
                if 'Member' in t['columns']:
                    code = str(row['Member'] or '')
                    if code.lower() == 'closed':
                        status = 'Inactive'
                row['dcc_status'] = status
                row['dcc_stamp'] = stamp
