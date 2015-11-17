import argparse
import json
import os
import sheetsite
import shutil
import subprocess

# States:
#   .pending -> will need to be processed
#   .processing -> working on it
#   .ack_pending -> will need to be acknowledged
#   .ack_processing -> working on acking

def run():
    parser = argparse.ArgumentParser(description='Update a website from a spreadsheet. '
                                     'Take a spreadsheet (from google sheets or locally), and '
                                     'convert it to a .json file that a static website '
                                     'generator like jekyll can use, then push it out.')
    parser.add_argument('layout_file', nargs="?", help='json file '
                        'describing source, destination, and all settings')
    parser.add_argument('--cache', nargs=1, required=False, default='cache',
                        help='cache directory where work is stored.')
    parser.add_argument('--spool', nargs=1, required=False,
                        help='if supplied, work only on sheets mentioned in this directory.'
                        '(see sheetmail)')
    args = parser.parse_args()
    if args.layout_file is None:
        print "Need a layout file, I should give you an example."
        print "See example_sites.json in github repository for sheetsite."
        print "Add -h for help."
        exit(1)

    layout = json.loads(open(args.layout_file).read())
    root = args.cache[0]
    spool = args.spool[0]

    names = layout['names']

    for name in names:

        site = layout['sites'][name]

        source = site['source']
        if source['name'] != 'google-sheets':
            print "do not know how to read from", source['name']
            exit(1)

        if spool is not None:
            key = source['key']
            pending_file = os.path.join(spool, '{}.pending.json'.format(key))
            processing_file = os.path.join(spool, '{}.processing.json'.format(key))
            present = False
            if os.path.exists(pending_file):
                shutil.move(pending_file, processing_file)
                present = True
            if os.path.exists(processing_file):
                present = True
            if not present:
                continue

        path = os.path.join(root, name)
        if not(os.path.exists(path)):
            os.makedirs(path)

        from sheetsite.google_spreadsheet import GoogleSpreadsheet
        from sheetsite.site import Site
        wb = GoogleSpreadsheet()
        wb.connect(source['credential_file'])
        wb.load_remote(source['key'])

        ss = Site(wb, os.path.join(path, 'geocache.sqlite'))
        if 'flags' in site:
            ss.configure(site['flags'])
        output_file = os.path.join(path, 'public.json')
        private_output_file = os.path.join(path, 'private.json')
        ss.save_local(output_file)
        ss.save_local(private_output_file, private_sheets=True)

        destination = site['destination']
        if destination['name'] != 'git':
            print "do not know how to write to", destination['name']
            exit(1)

        local_repo = os.path.join(path, 'repo')
        if not(os.path.exists(local_repo)):
            subprocess.check_output(['git', 'clone', destination['repo'], local_repo])
        wd = os.getcwd()
        os.chdir(local_repo)
        subprocess.check_output(['git', 'pull'])
        os.chdir(wd)
        shutil.copyfile(output_file, os.path.join(local_repo, destination['file']))
        os.chdir(local_repo)
        subprocess.check_output(['git', 'add', destination['file']])
        try:
            subprocess.check_output(['git', 'commit', '-m', 'update from sheetsite'])
            subprocess.check_output(['git', 'push'])
        except subprocess.CalledProcessError:
            print "Commit/push skipped"
        os.chdir(wd)

        if spool is not None:
            key = source['key']
            processing_file = os.path.join(spool, '{}.processing.json'.format(key))
            ack_pending_file = os.path.join(spool, '{}.ack_pending.json'.format(key))
            if os.path.exists(processing_file):
                shutil.move(processing_file, ack_pending_file)
