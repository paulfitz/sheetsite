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

## Usage for local spreadsheet

1. Run `sheetsite spreadsheet.xlsx output.json`

2. Use `output.json` as data for static website (see http://jekyllrb.com/docs/datafiles/ for example).

## Usage for google sheet

1. [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html) - thanks to gspread developers for creating this documentation!

2. Find the name or url of the sheet you care about.

3. Make sure you share the sheet with the email address in the OAuth2 credentials.  Read-only permission is fine.

4. Run `sheetsite --credential credential.json "Name of spreadsheet" output.json`

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

