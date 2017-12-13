import csv


class CsvSpreadsheet(object):

    def __init__(self, filename):
        with open(filename, 'r') as fin:
            reader = csv.reader(fin)
            self.data = [row for row in reader]

    def worksheets(self):
        return [self]

    def get_all_values(self):
        return self.data

    @property
    def title(self):
        return "sheet"
