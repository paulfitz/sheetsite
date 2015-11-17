from sheetsite.queue import app
import json
import os
import shutil
import subprocess
import daff
import premailer
import jinja2
import re

@app.task
def add(x, y):
    return x + y

@app.task
def notify_one(email, subject, name, page):
    print("tell %s about %s" % (email, name))
    import yagmail
    yag = yagmail.SMTP(os.environ['GMAIL_USERNAME'],
                       os.environ['GMAIL_PASSWORD'])
    import re
    if re.search(r'paulfitz', email):
        print("send [%s] / %s / %s" % (email, subject, page))
        print(type(email))
        yag.send(email, subject, contents = page)
        # print "not actually emailing"
    else:
        print("skip %s" % email)
    return True

@app.task
def notify_all(key, params, source, name, site_params, diff_html):
    print("NOTIFY_spreadsheet", key, params, source, name)

    root = app.conf['SHEETSITE_CACHE']
    path = os.path.join(root, name)
    print("Should look in", path)
    notifications = None
    for fname in ['private.json', 'public.json']:
        full_fname = os.path.join(path, fname)
        print("Look in", full_fname)
        book = json.loads(open(full_fname).read())
        if 'notifications' in book['tables']:
            notifications = book['tables']['notifications']
            break
    if notifications is None:
        print("No notifications requested")
        return True
    print("Notifications", notifications)

    # make a html report
    css = daff.DiffRender().sampleCss()
    site_params = dict(site_params)
    site_params['css'] = css
    site_params['diff'] = diff_html
    env = jinja2.Environment(loader=jinja2.PackageLoader('sheetsite', 'templates'))
    template = env.get_template('update.html')
    page = template.render(site_params)
    page = premailer.transform(page)

    for target in notifications['rows']:
        email = target.get('EMAIL', None)
        if email is None:
            email = target.get('email', None)
        if email is not None:
            notify_one.delay(email=email,
                             subject="update to " + name,
                             name=name,
                             page=page)

    return True

@app.task
def update_spreadsheet(key, params, path, source, destination, site, name):

    site_params = {
        'name': params.get('title', 'unknown'),
        'sheet_link': source.get('link', None),
        'site_link': destination.get('link', None)
    }

    from sheetsite.google_spreadsheet import GoogleSpreadsheet
    from sheetsite.site import Site
    wb = GoogleSpreadsheet()
    wb.connect(source['credential_file'])
    wb.load_remote(source['key'])

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

    if destination['name'] == 'git':
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
            print("Commit/push skipped")
        os.chdir(wd)

    # compute changes
    io = daff.TableIO()
    dapp = daff.Coopy(io)
    t1 = dapp.loadTable(prev_raw_file)
    t2 = dapp.loadTable(raw_file)
    diff_html = daff.diffAsHtml(t1,t2)

    notify_all.delay(key=key, 
                     params=params, 
                     source=source, 
                     name=name,
                     site_params=site_params,
                     diff_html=diff_html)
    return True


@app.task
def handle_spreadsheet_update(key, params):
    print("PROCESS_spreadsheet", key, params)

    layout = json.loads(open(app.conf['SHEETSITE_LAYOUT']).read())
    root = app.conf['SHEETSITE_CACHE']

    names = layout['names']

    for name in names:

        site = layout['sites'][name]

        source = site['source']
        if source['name'] != 'google-sheets':
            print("do not know how to read from", source['name'])
            return False

        destination = site['destination']
        if destination['name'] != 'git' and destination['name'] is not None:
            print("do not know how to write to", destination['name'])
            return False

        if key != source['key']:
            continue

        path = os.path.join(root, name)
        if not(os.path.exists(path)):
            os.makedirs(path)

        update_spreadsheet.delay(key, params, path, source, destination, site, name)


    return False

