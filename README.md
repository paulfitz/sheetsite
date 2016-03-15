# sheetsite: sheets for sites

[![Build Status](https://travis-ci.org/paulfitz/sheetsite.svg?branch=master)](https://travis-ci.org/paulfitz/sheetsite)
[![PyPI version](https://badge.fury.io/py/sheetsite.svg)](http://badge.fury.io/py/sheetsite)

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

## Google sheet to local json

Place a file named `_sheetsite.yml` in a directory, in this format:

```yaml
source:
  name: google-sheets
  key: 15Vs_VGpupeGkljceEow7q1ig447FJIxqNS1Dd0dZpFc
  credential_file: service.json

destination:
  file: _data/directory.json
```

The file should have two stanzas, `source` specifying where to get
data from, and `destination` specifying where to put it.  This
examples reads a private google spreadsheet and saves it as
`_data/directory.json`.  The key comes from the url of the spreadsheet.
The credentials file is something you [get from google](http://gspread.readthedocs.org/en/latest/oauth2.html).

You could now build a static website from that `.json`, see
http://jekyllrb.com/docs/datafiles/ for how.  For example,
the map at http://datacommons.coop/tap/ is of data pulled
from a google spreadsheet, styled using
https://github.com/datacommons/tap via github pages.

## Strip private sheets, columns, or cells

By default, sheetsite will strip:

* Any columns whose name is in parentheses, e.g. `(Private Notes)`
* Any cells or text within cells surrounded by double parentheses, e.g. `((private@email.address))`
* Any sheets whose name is in double parentheses, e.g. `((secret sheet))`

## Geocoding

If you have a table with a column called `address`, sheetsite can geocode it for
you and pass along the results.  Just add the following in your yaml:

```
flags:
  add:
    table_name_goes_here:
      - latitude
      - longitude
      - country
      - state
      - city
      - street
      - zip
```

You can add just the columns you want.  Geocoding results are cached in a `_cache`
directory by default so they do not need to be repeated in future calls to sheetsite.

The full list of columns (with synonyms) available is:
  * latitude / lat
  * longitude / lng
  * latlng
  * country
  * state / province / region
  * city / locality
  * street
  * zip / postal_code

Normally you won't actually have a stand-alone `address` column.  More usually,
information will be spread over multiple columns, or some will be implicit (e.g.
the state/province and country).  You can tell sheetsite how to construct addresses
for geocoding by listing columns and constants to build it from.  For example:

```
flags:
  address:
    table_name_goes_here:
      - street_address1
      - street_address2
      - city
      - Manitoba
      - Canada
  add:
    table_name_goes_here:
      - postal_code
```

This tells sheetsite to produce addresses of the form:
```
<street_address1> <street_address2> <city> Manitoba Canada
```
And add a `postal_code` column populated by geocoding.

It is possible to request columns directly in the spreadsheet.  Just
wrap the column name in square brackets, like `[state]` or `[zip]`.
Any blank cells in such columns will be filled using geocoding based
on the address given in that row.  If the address columns have not been
configured in `flags` then the address must be present in a single column
literally called `address`.


## Other formats

Other formats supported as destinations are `.xlsx` and `.xls`.  There
are also experimental plugins for writing to ftp, git, or particular
database schemas.

## Getting credentials

[Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html) - thanks to gspread developers for creating this documentation!

Make sure you share the sheet with the email address in the OAuth2 credentials.  Read-only permission is fine.

## License

sheetsite is distributed under the MIT License.

