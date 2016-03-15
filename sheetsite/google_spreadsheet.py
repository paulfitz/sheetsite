import gspread
import json

class GoogleSpreadsheet(object):

    def __init__(self):
        self.connection = None
        self.workbook = None

    def connect(self, credential_file):
        print "BOING", credential_file
        if credential_file:
            from oauth2client.client import SignedJwtAssertionCredentials
            json_key = json.load(open(credential_file))
            scope = ['https://spreadsheets.google.com/feeds']
            credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                                        json_key['private_key'].encode('ascii'), scope)
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
