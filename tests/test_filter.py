import json
from sheetsite.json_spreadsheet import JsonSpreadsheet
from sheetsite.site import Site

def test_filter():
    wb = JsonSpreadsheet('tests/configs/things.json')
    site = Site(wb)

    filtered_wb = site.public_workbook()
    result = wb.as_dict(filtered_wb)
    columns = result["tables"]["countries"]["columns"]
    assert "country" in columns
    assert not "opinion" in columns
    assert not "secret" in result["tables"]

    filtered_wb = site.private_workbook()
    result = wb.as_dict(filtered_wb)
    assert "secret" in result["tables"]
