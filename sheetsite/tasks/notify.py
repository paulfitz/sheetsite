from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
from sheetsite.site_queue import app
import smtplib


@app.task
def notify_one(email, subject, page, text):

    print("send [%s] / %s / %s" % (email, subject, page))

    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo()  # optional, called by login()
    me = os.environ['GMAIL_USERNAME']
    server_ssl.login(me, os.environ['GMAIL_PASSWORD'])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = email

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(page, 'html')

    msg.attach(part1)
    msg.attach(part2)

    server_ssl.sendmail(me, email, msg.as_string())
    server_ssl.close()

    return True


@app.task
def notify_all(name, site_params, diff_html, diff_text):
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
    site_params['diff'] = diff_text
    template = env.get_template('update.txt')
    page_text = template.render(site_params)

    for target in notifications['rows']:
        email = target.get('EMAIL', None)
        if email is None:
            email = target.get('email', None)
        if email is not None:
            if site_params['no_notify']:
                print("skip email to {}".format(email))
            else:
                notify_one.delay(email=email,
                                 subject="update to {}".format(site_params.get('name',
                                                                               'directory')),
                                 page=page,
                                 text=page_text)

    return True
