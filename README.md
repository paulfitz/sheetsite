```
pip install sheetsite
```


```
Please call as:
  sheetsite.py 2LvBgFeYzI9GeN2PTn5klcwBFFFeROlbwvTVF2qAIuBk credential.json save.xls
To:
  fetch a google spreadsheet with the given key (found in url)
  using the given authentication information
    (see http://gspread.readthedocs.org/en/latest/oauth2.html)
    (and don't forget to share the spreadsheet with client_email)
  saving to the named .xls or .json file.
Caveat:
  When saving to xls, the file will not retain original formatting.
  When saving to json, the first row is assumed to contain column names.
```
