import json
import os
from sheetsite.expand import load_config
from sheetsite.site_queue import app
from sheetsite.tasks.update_site import update_site


@app.task
def detect_site(params):
    key = params['key']
    print("PROCESS_spreadsheet", key, params)

    if os.path.isdir(os.environ['SHEETSITE_LAYOUT']):
        from glob import glob
        files = glob(os.path.join(os.environ['SHEETSITE_LAYOUT'], '*.yml'))
        files += glob(os.path.join(os.environ['SHEETSITE_LAYOUT'], '*.json'))
        layout = {
            'names': [],
            'sites': {}
        }
        for fname in files:
            name = os.path.splitext(os.path.split(fname)[1])[0]
            layout['names'].append(name)
            layout['sites'][name] = load_config(fname)
    else:
        # old big json file
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

