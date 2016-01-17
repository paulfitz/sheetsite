import os
from sheetsite.chain import apply_chain, compute_diff
from sheetsite.queue import app
from sheetsite.site import Site
from sheetsite.source import read_source
from sheetsite.destination import write_destination
from sheetsite.tasks.notify import notify_all
import shutil

@app.task
def update_site(params, path, site, name):

    source = site['source']
    destination = site['destination']

    site_params = {
        'name': params.get('title', 'unknown'),
        'sheet_link': source.get('link', None),
        'site_link': destination.get('link', None)
    }

    files = apply_chain(site, path)
    diff_html = compute_diff(files)

    notify_all.delay(name=name,
                     site_params=site_params,
                     diff_html=diff_html)
    return True


