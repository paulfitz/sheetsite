def read_source_excel(source):
    from sheetsite.xls_spreadsheet import XlsSpreadsheet
    wb = XlsSpreadsheet(source['filename'])
    return wb

