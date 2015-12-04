def read_source_json(source):
    from sheetsite.json_spreadsheet import JsonSpreadsheet
    wb = JsonSpreadsheet(source['filename'])
    return wb
