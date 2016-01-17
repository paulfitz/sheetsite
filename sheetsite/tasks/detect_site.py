import json
import os
from sheetsite.queue import app
from sheetsite.tasks.update_site import update_site

@app.task
def detect_site(params):
    key = params['key']
    print("PROCESS_spreadsheet", key, params)

    layout = json.loads(open(os.environ['SHEETSITE_LAYOUT']).read())
    root = os.environ['SHEETSITE_CACHE']

    names = layout['names']

    for name in names:

        site = layout['sites'][name]

        if key != site['source']['key']:
            continue

        path = os.path.join(root, name)
        if not(os.path.exists(path)):
            os.makedirs(path)

        update_site.delay(params, path, site, name)

    return False

