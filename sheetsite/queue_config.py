BROKER_URL = 'redis://localhost'
CELERY_RESULT_BACKEND = 'redis://localhost'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

SHEETSITE_LAYOUT = 'example_sites.json'

SHEETSITE_CACHE = '/cache/sites/'
