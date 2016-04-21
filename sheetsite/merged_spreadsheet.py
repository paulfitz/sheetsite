class MergedSpreadsheet(object):
    def __init__(self, workbook, merge_tables):
        self.workbook = workbook
        merged = set()
        for key, lst in merge_tables.items():
            merged = merged | set(lst)
        original_sheets = self.workbook.worksheets()
        sheet_by_name = {}
        for sheet in original_sheets:
            sheet_by_name[sheet.title] = sheet
        sheets = [sheet for sheet in original_sheets if sheet.title not in merged and '*' not in merged]
        for key, lst in merge_tables.items():
            if lst[0] == '*':
                sheets.append(MergedSheet(key, original_sheets))
            else:
                sheets.append(MergedSheet(key, [sheet_by_name[name] for name in lst]))
        self.sheets = sheets

    def worksheets(self):
        return self.sheets

class MergedSheet(object):
    def __init__(self, name, sheets):
        self.sheets = sheets
        self.name = name

    def get_all_values(self):
        rows = []
        for sheet in self.sheets:
            rows += sheet.get_all_values()
        deduped_rows = []
        keys = {}
        for row in rows:
            # I hate near dupes!!!!!
            rowx = [row[0], row[3]]
            # I hate python 2.7
            key = ' // '.join(str((x or '').encode('utf-8')) for x in rowx)
            import re
            key = re.sub(r'[\n\r ]+', ' ', key)
            if key not in keys:
                deduped_rows.append(row)
                keys[key] = True
        return deduped_rows

    @property
    def title(self):
        return self.name

