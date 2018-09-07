import daff
import os
from sheetsite.ids import process_ids
from sheetsite.site import Site
from sheetsite.source import read_source
from sheetsite.destination import write_destination
import shutil


def apply_chain(site, path):

    if not(os.path.exists(path)):
        os.makedirs(path)

    source = site['source']
    destination = site['destination']
    tweaks = site.get('tweaks')

    wb = None

    raw_file = os.path.join(path, 'raw.json')
    if 'cache' in source:
        wb = read_source({
            'filename': raw_file
        })
    else:
        wb = read_source(source)

    ss = Site(wb, os.path.join(path, 'geocache.sqlite'))
    if 'flags' in site:
        ss.configure(site['flags'])
    output_file = os.path.join(path, 'public.json')
    prev_raw_file = os.path.join(path, 'prev_raw.json')
    private_output_file = os.path.join(path, 'private.json')
    id_file = os.path.join(path, 'ids.json')
    prev_id_file = os.path.join(path, 'prev_ids.json')
    if os.path.exists(raw_file):
        shutil.copyfile(raw_file, prev_raw_file)
        if os.path.exists(id_file):
            shutil.copyfile(id_file, prev_id_file)

    ss.save_local(raw_file, enhance=False)

    ids = process_ids(prev_raw_file, raw_file, prev_id_file, id_file)
    ss.add_ids(ids)

    state = {
        'path': path,
        'output_file': output_file,
        'id_file': id_file
    }

    if tweaks:
        import json
        wj = json.load(open(raw_file, 'r'))
        for tweak, params in tweaks.items():
            print("Working on tweak", json.dumps(tweak))
            if 'tweak' in params:
                tweak = params['tweak']
            import importlib
            mod = importlib.import_module('sheetsite.tweaks.{}'.format(tweak))
            ct = 2
            try:
                target = mod.apply3
                ct = 3
            except AttributeError:
                target = mod.apply
            if ct == 3:
                target(wj, params, state)
            else:
                target(wj, params)
        from sheetsite.json_spreadsheet import JsonSpreadsheet
        ss.workbook = JsonSpreadsheet(None, data=wj)

    ss.save_local(output_file)
    if not os.path.exists(prev_raw_file):
        # once daff can cope with blank tables correctly, switch to this
        # with open(prev_raw_file, 'w') as fout:
        #    fout.write('{ "names": [], "tables": [] }')
        shutil.copyfile(raw_file, prev_raw_file)
        shutil.copyfile(id_file, prev_id_file)
    ss.save_local(private_output_file, private_sheets=True)

    state['workbook'] = ss.public_workbook()

    write_destination(destination, state)

    return {
        'prev_raw_file': prev_raw_file,
        'raw_file': raw_file
    }


def compute_diff(files, format='html'):
    io = daff.TableIO()
    dapp = daff.Coopy(io)
    t1 = dapp.loadTable(files['prev_raw_file'])
    t2 = dapp.loadTable(files['raw_file'])
    if format == 'both':
        r1 = daff.diffAsHtml(t1, t2)
        r2 = daff.diffAsAnsi(t1, t2)
        return (r1, r2)
    if format == 'html':
        return daff.diffAsHtml(t1, t2)
    return daff.diffAsAnsi(t1, t2)
