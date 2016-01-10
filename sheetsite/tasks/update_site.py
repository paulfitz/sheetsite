import daff
import os
from sheetsite.chain import apply_chain
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

    # compute changes
    io = daff.TableIO()
    dapp = daff.Coopy(io)
    t1 = dapp.loadTable(files['prev_raw_file'])
    t2 = dapp.loadTable(files['raw_file'\)
    diff_html = daff.diffAsHtml(t1,t2)

    notify_all.delay(name=name,
                     site_params=site_params,
                     diff_html=diff_html)
    return True


