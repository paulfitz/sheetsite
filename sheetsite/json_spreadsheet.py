from collections import OrderedDict
import json


class JsonSpreadsheet(object):

    def __init__(self, filename, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = json.load(open(filename))
        self.sheets = [JsonSheet(n, self.data['tables'][n])
                       for n in self.data['names']]

    def worksheets(self):
        return self.sheets

    @classmethod
    def as_dict(cls, workbook):
        result = OrderedDict()
        order = result['names'] = []
        sheets = result['tables'] = OrderedDict()
        for sheet in workbook.worksheets():
            title = sheet.title
            order.append(title)
            ws = sheets[title] = OrderedDict()
            vals = sheet.get_all_values()
            if len(vals) > 0:
                columns = vals[0]
                rows = vals[1:]
                ws['columns'] = columns
                ws['rows'] = [OrderedDict(zip(columns, row)) for row in rows]
            else:
                ws['columns'] = []
                ws['rows'] = []
        return result


class JsonSheet(object):

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.columns = data['columns']

    def get_all_values(self):
        results = [self.columns]
        for row in self.data['rows']:
            results.append([row[c] for c in self.columns])
        return results

    @property
    def title(self):
        return self.name

