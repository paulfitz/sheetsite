import json
from sheetsite.json_spreadsheet import JsonSpreadsheet

def write_destination_json(params, state):
    workbook = state['workbook']
    output_file = params['output_file']
    result = JsonSpreadsheet.as_dict(workbook)
    if output_file == None:
        print(json.dumps(result, indent=2))
    else:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    return True
