import json

def write_destination_json(params, state):
    from collections import OrderedDict
    workbook = state['workbook']
    output_file = params['output_file']
    result = OrderedDict()
    order = result['names'] = []
    sheets = result['tables'] = OrderedDict()
    for sheet in workbook.worksheets():
        title = sheet.title
        order.append(title)
        ws = sheets[title] = OrderedDict()
        vals = sheet.get_all_values()
        if len(vals)>0:
            columns = vals[0]
            rows = vals[1:]
            ws['columns'] = columns
            ws['rows'] = [OrderedDict(zip(columns, row)) for row in rows]
        else:
            ws['columns'] = []
            ws['rows'] = []
    if output_file == None:
        print(json.dumps(result, indent=2))
    else:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    return True
