import json
import os
from sheetsite.chain import apply_chain
from sheetsite.cmdline import run

########################################################
## python2 doesn't have TemporaryDirectory
## replacement begins

import contextlib
import os
import shutil
import tempfile

@contextlib.contextmanager
def TemporaryDirectory():
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath)

## replacement ends
## python2 doesn't have TemporaryDirectory
########################################################


def test_json_to_json_cmdline():
    with TemporaryDirectory() as temp_dir:
        os.environ['TEST_DIR'] = temp_dir
        run(['--config', 'tests/configs/json_to_json.json', '--cache-dir', temp_dir])


def test_json_to_json():
    with TemporaryDirectory() as temp_dir:
        target = "{}/out.json".format(temp_dir)
        params = {
            "source": { "filename": "tests/configs/things.json" },
            "destination": { "output_file": target }
        }
        apply_chain(params, temp_dir)
        with open(target, 'r') as f:
            data = json.load(f)
        assert len(data["tables"]["countries"]["columns"]) == 2
        assert data["tables"]["countries"]["rows"][1]["code"] == ""


def test_fill():
    with TemporaryDirectory() as temp_dir:
        target = "{}/out.json".format(temp_dir)
        params = {
            "source": { "filename": "tests/configs/fill.json" },
            "flags": {
                "geocoder": "dummy",
                "address": { "countries": ["country"] }
            },
            "destination": { "output_file": target }
        }
        apply_chain(params, temp_dir)
        with open(target, 'r') as f:
            data = json.load(f)
        assert data["tables"]["countries"]["rows"][0]["zip"] == "PO-STAL"

def test_single_to_multiple_add():
    with TemporaryDirectory() as temp_dir:
        target = "{}/out.json".format(temp_dir)
        params = {
            "source": { "filename": "tests/configs/things.json" },
            "flags": {
                "geocoder": "dummy",
                "address": { "countries": ["country"] },
                "add": { "countries": ["city", "address"] }
            },
            "destination": { "output_file": target }
        }
        apply_chain(params, temp_dir)
        with open(target, 'r') as f:
            data = json.load(f)
        assert data["tables"]["countries"]["rows"][0]["city"] == "Cityville"
        assert data["tables"]["countries"]["rows"][0]["address"] == "United Kingdom"
        assert data["tables"]["countries"]["rows"][1]["address"] == "United States"


def test_multiple_to_multiple_add():
    with TemporaryDirectory() as temp_dir:
        target = "{}/out.json".format(temp_dir)
        params = {
            "source": { "filename": "tests/configs/things.json" },
            "flags": {
                "geocoder": "dummy",
                "address": { "countries": ["code", "country", "Earth"] },
                "add": { "countries": ["city", "address"] }
            },
            "destination": { "output_file": target }
        }
        apply_chain(params, temp_dir)
        with open(target, 'r') as f:
            data = json.load(f)
        assert data["tables"]["countries"]["rows"][0]["city"] == "Cityville"
        assert data["tables"]["countries"]["rows"][0]["address"] == "uk United Kingdom Earth"

