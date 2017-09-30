from sheetsite.site_queue import app
from sheetsite.site import Site
import sheetsite.tasks.notify
import sheetsite.tasks.update_site
import sheetsite.tasks.detect_site


@app.task
def add(x, y):
    return x + y


