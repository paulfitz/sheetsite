from sheetsite.queue import app
from sheetsite.site import Site
from sheetsite.source import read_source
from sheetsite.destination import write_destination
import json
import os
import shutil
import subprocess
import daff
import premailer
import jinja2
import re

import sheetsite.tasks.notify
import sheetsite.tasks.update_site
import sheetsite.tasks.detect_site

@app.task
def add(x, y):
    return x + y


