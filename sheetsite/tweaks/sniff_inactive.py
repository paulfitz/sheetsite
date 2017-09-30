
def apply(wb, params):
    table = params.get('table')
    for name, t in wb['tables'].items():
        if name == table or table is None:
            if 'dcc_status' not in t['columns']:
                t['columns'].append('dcc_status')
            for row in t['rows']:
                status = None
                if 'NOTES' in t['columns']:
                    code = str(row['NOTES'] or '')
                    if 'DELETE' in code:
                        status = 'Inactive'
                if 'Active' in t['columns']:
                    code = str(row['Active'] or '')
                    if code == 'no':
                        status = 'Inactive'
                row['dcc_status'] = status
