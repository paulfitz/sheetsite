from celery import Celery
import os

app = Celery('sheetsite',
             broker=os.environ['SHEETSITE_BROKER_URL'],
             backend=os.environ['SHEETSITE_RESULT_BACKEND'],
             include=['sheetsite.tasks'])

if __name__ == '__main__':
    app.start()
