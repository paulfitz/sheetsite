import json

class JsonSpreadsheet(object):

    def __init__(self, filename):
        self.data = json.load(open(filename))
        self.sheets = [JsonSheet(n, self.data['tables'][n]) for n in self.data['names']]

    def worksheets(self):
        return self.sheets


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

