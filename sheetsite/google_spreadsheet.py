try:
    import pygsheets as gspread
    simple_auth = True
except ImportError:
    import gspread
    simple_auth = False


class GoogleSpreadsheet(object):

    def __init__(self):
        self.connection = None
        self.workbook = None

    def connect(self, credential_file):
        if simple_auth:
            self.connection = gspread.authorize(service_file=credential_file)
            return
        if credential_file:
            from oauth2client.service_account import ServiceAccountCredentials
            scope = ['https://spreadsheets.google.com/feeds']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope)
            self.connection = gspread.authorize(credentials)
        else:
            # rely on gspread_public fork
            self.connection = gspread.public()

    def load_remote(self, spreadsheet):
        try:
            self.workbook = self.connection.open(spreadsheet)
        except gspread.exceptions.SpreadsheetNotFound:
            try:
                self.workbook = self.connection.open_by_url(spreadsheet)
            except gspread.exceptions.NoValidUrlKeyFound:
                self.workbook = self.connection.open_by_key(spreadsheet)

    def worksheets(self):
        return self.workbook.worksheets()
