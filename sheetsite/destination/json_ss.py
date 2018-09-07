import json
from sheetsite.jsonify import dump, dumps
from sheetsite.json_spreadsheet import JsonSpreadsheet


def write_destination_json(params, state):
    workbook = state['workbook']
    output_file = params['output_file']
    result = JsonSpreadsheet.as_dict(workbook)
    if output_file is None:
        print(dumps(result, indent=2))
    else:
        with open(output_file, 'w') as f:
            dump(result, f, indent=2)
    return True
