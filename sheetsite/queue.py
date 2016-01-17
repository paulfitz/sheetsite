from celery import Celery
import os

app = Celery('sheetsite',
             broker=os.environ.get('SHEETSITE_BROKER_URL', None),
             backend=os.environ.get('SHEETSITE_RESULT_BACKEND', None),
             include=['sheetsite.tasks'])

if __name__ == '__main__':
    app.start()
