from celery import Celery

app = Celery('sheetsite',
             include=['sheetsite.tasks'])

app.config_from_object('sheetsite.queue_config')

if __name__ == '__main__':
    app.start()
