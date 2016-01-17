# sheetsite: sheets for sites

Manage your website or directory with a google sheet.

Features:

* Copy a private google sheet to local json (or excel).
* Strip specially marked columns or cells from the spreadsheet.
* (Optional) notify people with summary of updates.

Handy for keeping a static website up-to-date with information
kept in a google sheet, when not all of that information should 
be made public.

## Installation

```
pip install sheetsite
```

## Configuration

Place a file named '_sheetsite.yml' in a directory.  The file should have
two stanzas, `source` specifying where to get data from, and `destination`
specifying where to put it.  This examples reads private google spreadsheet
and saves it as `_data/directory.json`.

```yaml
source:
  name: google-sheets
  key: 15Vs_VGpupeGkljceEow7q1ig447FJIxqNS1Dd0dZpFc
  credential_file: service.json

destination:
  output_file: _data/directory.json
```

You could now build a static website from that `.json`, see http://jekyllrb.com/docs/datafiles/
for how (this is where the name of sheetsite comes from).

Other formats supported as destinations are `.xlsx` and `.xls`.  You can also read
from a local spreadsheet:

```yaml
source:
  filename: test.xlsx
```

## Getting credentials

[Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html) - thanks to gspread developers for creating this documentation!

Make sure you share the sheet with the email address in the OAuth2 credentials.  Read-only permission is fine.

## Privacy

By default, sheetsite will strip:

* Any columns whose name is in parentheses, e.g. `(Private Notes)`
* Any cells or text within cells surrounded by double parentheses, e.g. `((private@email.address))`
* Any sheets whose name is in double parentheses, e.g. `((secret sheet))`

## Geography

If you have a sheet with a column called `address`, then sheetsite can fill out
certain other columns automatically for you.  If you have a column called
`[latitude]` or `[longitude]`, any empty cells will be filled with data based
on the address.

## License

sheetsite is distributed under the MIT License.

