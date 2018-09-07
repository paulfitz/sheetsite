from collections import OrderedDict
import gspread
import json
import os
from oauth2client.client import SignedJwtAssertionCredentials
import re
from sheetsite.jsonify import dump


class Spreadsheet(object):

    def __init__(self, censor=True):
        self.connection = None
        self.workbook = None
        self.censor = censor

    def connect(self, credential_file):
        json_key = json.load(open(credential_file))
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                                    json_key['private_key'], scope)
        self.connection = gspread.authorize(credentials)

    def load_remote(self, spreadsheet_key):
        self.workbook = self.connection.open_by_key(spreadsheet_key)

    def save_local(self, output_file):
        _, ext = os.path.splitext(output_file)

        if ext == ".xls":
            return self.save_to_excel(output_file)
        elif ext == ".json":
            return self.save_to_json(output_file)

        print("Unknown extension", ext)
        return False

    def save_to_excel(self, output_file):
        import xlwt
        wb = xlwt.Workbook()
        for sheet in self.workbook.worksheets():
            ws = wb.add_sheet(sheet.title)
            rows = self.clean_cells(sheet.get_all_values())
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    ws.write(r, c, cell)
        wb.save(output_file)
        return True

    def save_to_json(self, output_file):
        result = OrderedDict()
        order = result['names'] = []
        sheets = result['tables'] = OrderedDict()
        for sheet in self.workbook.worksheets():
            order.append(sheet.title)
            ws = sheets[sheet.title] = OrderedDict()
            vals = self.clean_cells(sheet.get_all_values())
            columns = vals[0]
            rows = vals[1:]
            ws['columns'] = columns
            ws['rows'] = [OrderedDict(zip(columns, row)) for row in rows]
        with open(output_file, 'w') as f:
            dump(result, f, indent=2)
        return True

    def clean_cells(self, vals):
        hide_column = {}

        for idx, cell in enumerate(vals[0]):
            if len(cell) == 0 or cell[0] == '(':
                hide_column[idx] = True

        results = []

        for ridx, row in enumerate(vals):
            result = []
            for idx, cell in enumerate(row):
                if idx in hide_column:
                    continue
                cell = re.sub(r'\(\(.*\)\)', '', cell)
                cell = re.sub(r'[\n\r]+$', '', cell)
                cell = re.sub(r'^[\t \n\r]+$', '', cell)
                result.append(cell)
            results.append(result)

        return results

