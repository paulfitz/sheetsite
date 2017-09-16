import pygsheets


class GoogleSpreadsheet(object):

    def __init__(self):
        self.connection = None
        self.workbook = None

    def connect(self, credential_file):
        self.connection = pygsheets.authorize(service_file=credential_file)

    def load_remote(self, spreadsheet):
        self.workbook = self.connection.open_by_key(spreadsheet)

    def worksheets(self):
        return self.workbook.worksheets()
