def read_source_csv(source):
    from sheetsite.csv_spreadsheet import CsvSpreadsheet
    wb = CsvSpreadsheet(source['filename'])
    return wb
