import daff
import os
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

    wb = read_source(source)

    ss = Site(wb, os.path.join(path, 'geocache.sqlite'))
    if 'flags' in site:
        ss.configure(site['flags'])
    raw_file = os.path.join(path, 'raw.json')
    output_file = os.path.join(path, 'public.json')
    prev_raw_file = os.path.join(path, 'prev_raw.json')
    private_output_file = os.path.join(path, 'private.json')
    if os.path.exists(raw_file):
        shutil.copyfile(raw_file, prev_raw_file)

    ss.save_local(raw_file, enhance=False)
    ss.save_local(output_file)
    if not os.path.exists(prev_raw_file):
        shutil.copyfile(raw_file, prev_raw_file)
    ss.save_local(private_output_file, private_sheets=True)

    state = {
        'path': path,
        'output_file': output_file,
        'workbook': ss.public_workbook()
    }
    write_destination(destination, state)

    # compute changes
    io = daff.TableIO()
    dapp = daff.Coopy(io)
    t1 = dapp.loadTable(prev_raw_file)
    t2 = dapp.loadTable(raw_file)
    diff_html = daff.diffAsHtml(t1,t2)

    notify_all.delay(name=name,
                     site_params=site_params,
                     diff_html=diff_html)
    return True


