class FilteredSpreadsheet(object):
    def __init__(self, workbook, selector, processor):
        self.workbook = workbook
        titles = [(sheet, selector(sheet))
                  for sheet in self.workbook.worksheets()]
        self.sheets = [FilteredSheet(sheet, title, processor)
                       for sheet, title in titles
                       if title is not None]

    def worksheets(self):
        return self.sheets

    
class FilteredSheet(object):
    def __init__(self, sheet, title, processor):
        self.sheet = sheet
        self.name = title
        self.processor = processor

    def get_all_values(self):
        return self.processor(self.sheet, self.title)

    @property
    def title(self):
        return self.name

