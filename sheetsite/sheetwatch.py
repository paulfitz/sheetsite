import argparse
import dataset
import datetime
import imaplib
import json
import os
import re
import six
import sys
import time

try:
    from sheetsite.tasks.detect_site import detect_site
except ImportError as e:
    print(e)
    print("*** Did you pip install sheetsite[queue]?")
    exit(1)


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


class ImapMail(object):
    def __init__(self, parent, uid):
        self.parent = parent
        self.uid = uid
        self.subject = ""
        self.body = ""

    def plain(self, part):
        if isinstance(part, six.string_types):
            return part.encode('utf8', 'xmlcharrefreplace').strip()
        return part.as_string()

    def parse_header(self, part):
        if isinstance(part, six.string_types):
            return self.plain(part)
        elif isinstance(part, list):
            return " ".join([self.parse_header(p) for p in part])
        elif isinstance(part, tuple):
            return part[0]
        return part

    def parse_body(self, message):
        payload = message.get_payload(decode=True) or message.get_payload()
        if isinstance(payload, six.string_types):
            return self.plain(payload)
        elif isinstance(payload, list):
            for part in payload:
                if part.get_content_type() == 'text/plain':
                    return self.plain(part)
            return self.plain(payload[0])
        return message.as_string()
            
    def fetch(self):
        result, data = self.parent.mailer.uid('fetch', self.uid, '(RFC822)')
        raw_email = data[0][1]
        import email
        from email.header import decode_header
        email_message = email.message_from_string(raw_email.decode('utf-8'))

        def extract(key):
            return self.parse_header(decode_header(email_message[key]))
        self.subject = extract('Subject')
        self.body = self.parse_body(email_message)

    def has_label(self, label):
        return False

    def add_label(self, label):
        self.parent.set_processed(self.uid)


class ImapMailbox(object):
    def __init__(self, username, pword):
        self.mailer = imaplib.IMAP4_SSL('imap.gmail.com')
        self.db_name = os.path.join(os.environ['SHEETSITE_CACHE'],
                                    "emails.sqlite3")
        self.db_uri = "sqlite:///{}".format(self.db_name)
        print(self.db_uri)
        self.db = dataset.connect(self.db_uri)
        self.record = self.db['emails']
        import sqlalchemy.types
        if self.record.count() == 0:
            self.record.create_column('uid', sqlalchemy.types.Text)
            self.record.create_index(['uid'])
        self.login(username, pword)

    def login(self, username, pword):
        self.mailer.login(username, pword)

    def inbox(self):
        self.mailer.select('inbox')
        return self
    
    def set_processed(self, uid):
        self.record.insert({'uid': uid})
        
    def mail(self, **_):
        import datetime
        date = (datetime.date.today() - datetime.timedelta(10)).strftime("%d-%b-%Y")
        result, data = self.mailer.uid(
            'search', 
            None, 
            '(SENTSINCE {date} FROM "notify@google.com")'.format(
                date=date)
        )
        email_uids = data[0].split()
        mails = []
        for uid in email_uids:
            print("Checking", uid)
            if len(list(self.record.find(uid=uid))) == 0:
                print("Not processed yet!")
                mails.append(ImapMail(self, uid))
        return mails

    def logout(self):
        self.mailer.logout()


def worker():
    from celery.__main__ import main
    while len(sys.argv) > 0:
        sys.argv.pop()
    for arg in ['celery', '-A', 'sheetsite.site_queue', 'worker', '-l', 'info']:
        sys.argv.append(arg)
    sys.exit(main())


def run():

    parser = argparse.ArgumentParser(description='Check email for sheet change notifications.'
                                     'For when webhooks are not an option.')

    subparsers = parser.add_subparsers(dest='cmd')

    ping = subparsers.add_parser('ping')

    ping.add_argument('--clear', action='store_true',
                      help="do not take action on initial emails, just absorb them")

    ping.add_argument('--no-notify', action='store_true',
                      help="do not send notification emails")

    ping.add_argument('--delay', type=int, default=0,
                      help="delay in seconds between pings"
                      " (if not set, just one ping is made")

    subparsers.add_parser('worker')

    args = parser.parse_args()

    if args.cmd == 'worker':
        worker()
        return

    ignore = args.clear
    while True:
        # log in to gmail
        if 'GMAIL_PASSWORD' in os.environ:
            if os.environ['GMAIL_USERNAME'] == 'test':
                g = TestMailbox(os.environ['GMAIL_PASSWORD'])
            else:
                g = ImapMailbox(os.environ['GMAIL_USERNAME'],
                                os.environ['GMAIL_PASSWORD'])
        else:
            print("Need GMAIL_USERNAME/GMAIL_PASSWORD to be set in environment.")
            print("They should be set to whatever account receives change notications of sheet.")
            exit(1)

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
                if not ignore:
                    sheet['no_notify'] = args.no_notify
                    store_work(sheet)
                else:
                    print("  * ignoring this email as directed")
            msg.add_label('sheetmailed')

        # leave
        g.logout()

        if args.delay == 0:
            break

        ignore = False
        time.sleep(args.delay)


if __name__ == '__main__':
    run()
