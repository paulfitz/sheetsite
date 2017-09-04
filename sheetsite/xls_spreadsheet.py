from openpyxl import load_workbook


class XlsSpreadsheet(object):

    def __init__(self, filename):
        self.book = book = load_workbook(filename=filename)
        self.sheets = [XlsSheet(n, book.get_sheet_by_name(n)) for n in book.get_sheet_names()]

    def worksheets(self):
        return self.sheets


class XlsSheet(object):

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def get_all_values(self):
        input = self.data.rows
        output = []
        for i, row in enumerate(input):
            output_row = []
            output.append(output_row)
            for j, cell in enumerate(row):
                output_row.append(cell.value)
        return output

    @property
    def title(self):
        return self.name

