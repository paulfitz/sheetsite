# sheetsite: sheets for sites

[![Build Status](https://travis-ci.org/paulfitz/sheetsite.svg?branch=master)](https://travis-ci.org/paulfitz/sheetsite)
[![PyPI version](https://badge.fury.io/py/sheetsite.svg)](http://badge.fury.io/py/sheetsite)

Keep a website or directory in sync with a google sheet.

Features:

* Copy a google spreadsheet locally, as json or excel format.
* Can strip specified tabs, columns, or cells from the spreadsheet,
  in case not all of it should be copied along.
* Can push a filtered json copy out to a git repository, handy for
  maintaining a website based on a private shared spreadsheet.
* Can augment the sheet with geocoding, adding latitude and longitude based
  on address fields for example.
* Can notify people by email with a summary of updates.


## Installation

For the basics:

```
pip install sheetsite
```

For all bells and whistles, when automating a sheet-to-site workflow:

```
pip install sheetsite[queue]
```

## Specifying the source and destination

The `sheetsite` utility, when run without any arguments, will expect
to find all necessary options in a `_sheetsite.yml` file.  A simple
example of such a file is:

```yaml
source:
  name: google-sheets
  key: 15Vs_VGpupeGkljceEow7q1ig447FJIxqNS1Dd0dZpFc
  credential_file: service.json

destination:
  file: sheet.xlsx
```

The file should have two stanzas, `source` specifying where to get
data from, and `destination` specifying where to put it.  This
examples reads a private google spreadsheet and saves it as
`sheet.xlsx`.  The key comes from the url of the spreadsheet.
The credentials file is something you [get from google](https://pygsheets.readthedocs.io/en/latest/authorizing.html).

Here's an example that outputs json:

```yaml
source:
  name: google-sheets
  key: 15Vs_VGpupeGkljceEow7q1ig447FJIxqNS1Dd0dZpFc
  credential_file: service.json

destination:
  file: _data/directory.json
```

You could now build a static website from that `.json`, see
http://jekyllrb.com/docs/datafiles/ for how, or see an example
at https://github.com/datacommons/commoners

Here's an example that adds some geocoded fields and directly
updates a git repository:

```yaml
source:
  name: google-sheets
  key: 19UaXhqPQ0QHEfSWS_adDEtPwYstq8llK2YijpvFZcKA
  credential_file: service.json

flags:
  add:
    directory:
      - LAT
      - LNG
      - COUNTRY
      - STREET
      - REGION
      - LOCALITY

destination:
  name: git
  repo: git@github.com:datacommons/commoners
  file: _data/directory.json
```

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

## Row uuids

There's a random feature to add uuids to rows.   Just add a column
called `dccid` for some reason:

```
flags:
  add:
    table_name_goes_here:
      - dccid
```

A uuid will be added to each row.  A good faith effort will be made
to keep that uuid constant across updates, keeping it linked to the
row where it first appeared.

## Grouping locations

If there are several rows of a sheet that will give locations that should
be thought of as a single unit (e.g. an organization with multiple locations),
you can tell `sheetsite` about that.  To do so, give it a `group` key.
Every row for which the `group` is the same (and not blank) will be bound
together.  When geocaching, blank cells in address cells  will be filled
in with information from the first row in this group.  For example, with this
configuration:

```
flags:
  group: WEBSITE
```

Then for a table like the following:

```
STREET,   CITY,   STATE,    WEBSITE
...
17 N St,  Foo,    Utopia,   joe.ut
16 S St,  ,       ,         joe.ut
...

During geocoding, `16 S St` would be assumed to be in `Foo, Utopia`.

## Renaming columns

Columns can be renamed.  This will occur before any other operation.

```
flags:
  rename:
    table_name:
      old_column_name1: new_column_name1
      old_column_name2: new_column_name2
```

## Getting credentials

[Obtain credentials for accessing sheets from the Google Developers Console](https://pygsheets.readthedocs.io/en/latest/authorizing.html).

Make sure you share the sheet with the email address in the credentials file.  Read-only permission is fine.

## Examples

For example, the map at http://datacommons.coop/tap/ is a visualization
of data pulled from a google spreadsheet, styled using
https://github.com/datacommons/tap via github pages.

## sheetwatch

It can be useful to automate and forget `sheetsite`, so that updates
to a google spreadsheet propagate automatically to their final
destination.  The `sheetwatch` utility does this.  It requires a queue
server to operate.  To install, do:

```
pip install sheetsite[queue]
```

Install any queue server supported by `celery`.  For example, `redis`:

```
sudo apt-get install redis-server
redis-server
```

We need to set some environment variables to let `sheetwatch` know
where to find the queue server:

```
export SHEETSITE_BROKER_URL=redis://localhost
export SHEETSITE_RESULT_BACKEND=redis://localhost
```

The `sheetwatch` program needs a cache directory for its operations.

```
export SHEETSITE_CACHE=$HOME/cache/sites
```

Finally, it needs to know where there is a directory full of `yml`
files describing any sheets to monitor and their corresponding sites:

```
export SHEETSITE_LAYOUT=$PWD/sites/enabled
```

We now start a worker:

```
sheetwatch worker
```

The last thing we need to do is check a mailbox from time to time
for sheet change notifications from Google, and kick off site updates
as needed:

```
  export GMAIL_USERNAME=*****
  export GMAIL_PASSWORD=*****
sheetwatch ping --delay 60
```

## License

sheetsite is distributed under the MIT License.

