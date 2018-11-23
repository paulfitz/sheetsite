import json

class Sheets(object):

    def __init__(self, data):
        self.data = data

    @property
    def tables(self):
        return [self.table(name) for name in self.data['names']]

    def table(self, name):
        return Table(self.data['tables'][name], name)

    def tables_with_columns(self, *columns, require=True):
        lst = [self.table(name) for name in self.data['names']
                if set(columns) <= set(self.data['tables'][name]['columns'])]
        if require and len(lst) == 0:
            raise Exception('no table found with column(s) {}'.format(columns))
        return lst

    def __repr__(self):
        return json.dumps(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def __delitem__(self, key):
        del self.data[key]


class Table(object):
    def __init__(self, data, name):
        self.data = data
        self.name = name

    @property
    def columns(self):
        return self.data['columns']

    def has_column(self, name):
        return (name in self.columns)

    @property
    def rows(self):
        return [Row(row) for row in self.data['rows']]

    def add_column(self, name):
        if self.has_column(name):
            return
        self.data['columns'].append(name)
        for row in self.rows:
            row[name] = None

    def remove_column(self, name):
        if not self.has_column(name):
            return
        self.data['columns'] = [c for c in self.data['columns'] if c != name]
        for row in self.rows:
            del row[name]

    def __repr__(self):
        return json.dumps(self.data)

class Row(object):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def __delitem__(self, key):
        del self.data[key]

    def __repr__(self):
        return json.dumps(self.data)

    def add_to_set(self, key, val):
        if self.data[key] is None:
            self.data[key] = []
        if val not in self.data[key]:
            self.data[key].append(val)
