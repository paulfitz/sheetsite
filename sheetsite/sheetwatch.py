import argparse
import datetime
try:
    import gmail_client as gmail
    from sheetsite.tasks.detect_site import detect_site
except ImportError as e:
    print(e)
    print("*** Did you pip install sheetsite[queue]?")
    exit(1)
import json
import os
import re


def find_sheet(msg):
    key = None
    title = None
    who = None
    m = re.search(r'docs.google.com/spreadsheets/d/([^/]*)/', msg.body)
    if m:
        key = m.group(1)
    m = re.search(r'\"([^\"]*)', msg.subject)
    if m:
        title = m.group(1)
        title = re.sub(r'[\r\n]', '', title)
    m = re.search(r'[\r\n]\* (.*) made changes', msg.body)
    if m:
        who = m.group(1)
    if key is not None:
        print("Found %s: %s (%s)" % (key, title, who))
        return {
            "key": key,
            "title": title,
            "who": who
        }
    return None


def store_work(job):
    if 'key' not in job:
        return
    detect_site.delay(job)


class TestMail(object):
    def __init__(self, subject=None, body=None, labels=None):
        self.subject = subject
        self.body = body
        self.labels = labels

    def fetch(self):
        pass

    def has_label(self, label):
        return label in self.labels

    def add_label(self, label):
        if not self.has_label(label):
            self.labels.append(label)


class TestMailbox(object):
    def __init__(self, fname):
        self.fname = fname
        self.data = json.load(open(fname))

    def inbox(self):
        return self

    def mail(self, **_):
        return [TestMail(**x) for x in self.data]

    def logout(self):
        pass


def run():

    # log in to gmail
    if 'GMAIL_PASSWORD' in os.environ:
        if os.environ['GMAIL_USERNAME'] == 'test':
            g = TestMailbox(os.environ['GMAIL_PASSWORD'])
        else:
            g = gmail.login(os.environ['GMAIL_USERNAME'],
                            os.environ['GMAIL_PASSWORD'])
    else:
        print("Need GMAIL_USERNAME/GMAIL_PASSWORD to be set in environment.")
        print("They should be set to whatever account receives change notications of sheet.")
        exit(1)

    parser = argparse.ArgumentParser(description='Check email for sheet change notifications.'
                                     'For when webhooks are not an option.')

    parser.parse_args()

    # look for recent emails from google notify
    window = datetime.datetime.now() - datetime.timedelta(days=10)
    mail = g.inbox().mail(sender='notify@google.com', after=window)

    # check emails for action items
    keys = {}
    for msg in mail:
        msg.fetch()
        print(msg.subject)
        # msg.remove_label('sheetmailed')
        if msg.has_label('sheetmailed'):
            continue
        sheet = find_sheet(msg)
        if sheet is not None:
            if sheet['key'] in keys:
                sheet = None
            else:
                keys[sheet['key']] = True
        if sheet is not None:
            store_work(sheet)
        msg.add_label('sheetmailed')

    # leave
    g.logout()
