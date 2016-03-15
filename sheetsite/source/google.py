def read_source_google(source):
    from sheetsite.google_spreadsheet import GoogleSpreadsheet
    wb = GoogleSpreadsheet()
    wb.connect(source.get('credential_file', None))
    wb.load_remote(source['key'])
    return wb

