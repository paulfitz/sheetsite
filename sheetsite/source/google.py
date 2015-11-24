def read_source_google(source):
    from sheetsite.google_spreadsheet import GoogleSpreadsheet
    wb = GoogleSpreadsheet()
    wb.connect(source['credential_file'])
    wb.load_remote(source['key'])
    return wb

