import argparse
import json
import os
import sheetsite
import shutil
import subprocess

def run():
    parser = argparse.ArgumentParser(description='Update a website from a spreadsheet. '
                                     'Take a spreadsheet (from google sheets or locally), and '
                                     'convert it to a .json file that a static website '
                                     'generator like jekyll can use, then push it out.')
    parser.add_argument('layout_file', nargs="?", help='json file '
                        'describing source, destination, and all settings')
    parser.add_argument('--cache', nargs=1, required=False, default='cache',
                        help='cache directory where work is stored.')
    args = parser.parse_args()
    if args.layout_file is None:
        print "Need a layout file, I should give you an example."
        print "See example_sites.json in github repository for sheetsite."
        exit(1)

    layout = json.loads(open(args.layout_file).read())
    root = args.cache[0]

    names = layout['names']

    for name in names:

        site = layout['sites'][name]

        path = os.path.join(root, name)
        if not(os.path.exists(path)):
            os.makedirs(path)

        source = site['source']
        if source['name'] != 'google-sheets':
            print "do not know how to read from", source['name']
            exit(1)

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
