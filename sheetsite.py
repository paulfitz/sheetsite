#!/usr/bin/python

from collections import OrderedDict
import gspread
import json
import os
import sys
from oauth2client.client import SignedJwtAssertionCredentials


def save_to_excel(spreadsheet, output_file):
    import xlwt
    wb = xlwt.Workbook()
    for sheet in spreadsheet.worksheets():
        ws = wb.add_sheet(sheet.title)
        rows = sheet.get_all_values()
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                ws.write(r, c, cell)
    wb.save(output_file)


def save_to_json(spreadsheet, output_file):
    result = OrderedDict()
    order = result['names'] = []
    sheets = result['tables'] = OrderedDict()
    for sheet in spreadsheet.worksheets():
        order.append(sheet.title)
        ws = sheets[sheet.title] = OrderedDict()
        vals = sheet.get_all_values()
        columns = vals[0]
        rows = vals[1:]
        ws['columns'] = columns
        ws['rows'] = [OrderedDict(zip(columns, row)) for row in rows]
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)


def fetch_spreadsheet(spreadsheet_key, credential_file, output_file):

    json_key = json.load(open(credential_file))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                                json_key['private_key'], scope)

    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(spreadsheet_key)

    _, ext = os.path.splitext(output_file)

    if ext == ".xls":
        save_to_excel(sh, output_file)
    elif ext == ".json":
        save_to_json(sh, output_file)
    else:
        print("Unknown extension", ext)
        exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Please call as:")
        print("  sheetsite.py 2LvBgFeYzI9GeN2PTn5klcwBFFFeROlbwvTVF2qAIuBk credential.json save.xls")
        print("To:")
        print("  fetch a google spreadsheet with the given key (found in url)")
        print("  using the given authentication information")
        print("    (see http://gspread.readthedocs.org/en/latest/oauth2.html)")
        print("    (and don't forget to share the spreadsheet with client_email)")
        print("  saving to the named .xls or .json file.")
        print("Caveat:")
        print("  When saving to xls, the file will not retain original formatting.")
        print("  When saving to json, the first row is assumed to contain column names.")
        exit(1)
    spreadsheet_key = sys.argv[1]
    credential_file = sys.argv[2]
    output_file = sys.argv[3]
    fetch_spreadsheet(spreadsheet_key, credential_file, output_file)
