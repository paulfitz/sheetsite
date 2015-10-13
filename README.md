# sheetsite: sheets for sites

Manage your website or directory with a google sheet.

Features:

* Copy a private google sheet to local json (or excel).
* Strip specially marked columns or cells from the spreadsheet.

Handy for keeping a static website up-to-date with information
kept in a google sheet, when not all of that information should 
be made public.

## Usage

1. `pip install sheetsite`

2. [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html) - thanks to gspread developers for creating this documentation!

3. Find the key of the sheet you care about from its url (e.g. `2LvBgFe...F2qAIuBk`).

4. Make sure you share the sheet with the email address in the OAuth2 credentials.  Read-only permission is fine.

5. `sheetsite.py --credential credential.json 2LvBgFe...F2qAIuBk output.json` (or `output.xls`)

6. Build a website around the json, as for example http://datacommons.coop/tap/ = https://github.com/datacommons/tap

## Privacy

By default, sheetsite will strip:

* Any columns whose name is in parentheses, e.g. `(Private Notes)`
* Any cells or text within cells surrounded by double parentheses, e.g. `((private@email.address))`

## License

sheetsite is distributed under the MIT License.

