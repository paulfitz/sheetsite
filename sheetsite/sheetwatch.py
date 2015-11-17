from __future__ import absolute_import
import argparse
import datetime
import gmail_client as gmail
import json
import os
import re
from sheetsite.tasks import handle_spreadsheet_update

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
        print "Found %s: %s (%s)" % (key, title, who)
        return {
            "key": key,
            "title": title,
            "who": who
        }
    return None


def store_work(job):
    if not 'key' in job:
        return
    handle_spreadsheet_update.delay(job['key'], job)

def run():

    # log in to gmail
    if 'GMAIL_PASSWORD' in os.environ:
        g = gmail.login(os.environ['GMAIL_USERNAME'],
                        os.environ['GMAIL_PASSWORD'])
    else:
        print "Need GMAIL_USERNAME/GMAIL_PASSWORD to be set in environment"
        exit(1)

    parser = argparse.ArgumentParser(description='Check email for sheet change notifications.'
                                     'For when webhooks are not an option.')

    args = parser.parse_args()

    # look for recent emails from google notify
    window = datetime.datetime.now() - datetime.timedelta(days=30)
    mail = g.inbox().mail(sender='notify@google.com', after=window)

    # check emails for action items
    keys = {}
    for msg in mail:
        msg.fetch()
        print msg.subject
        msg.remove_label('sheetmailed')
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


