import json
import os
import re
from sheetsite.queue import app

@app.task
def notify_one(email, subject, page):
    print("tell %s about %s" % (email, subject))
    import yagmail
    yag = yagmail.SMTP(os.environ['GMAIL_USERNAME'],
                       os.environ['GMAIL_PASSWORD'])
    if True or re.search(r'paulfitz', email):
        print("send [%s] / %s / %s" % (email, subject, page))
        print(type(email))
        yag.send(email, subject, contents = page)
        # print "not actually emailing"
    else:
        print("skip %s" % email)
    return True

@app.task
def notify_all(name, site_params, diff_html):
    print("NOTIFY_spreadsheet", site_params, name)

    import daff
    import jinja2
    import premailer

    root = os.environ['SHEETSITE_CACHE']
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
                             subject="update to {}".format(site_params['name']),
                             page=page)

    return True
