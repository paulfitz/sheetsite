import json
import os
import unittest
from sheetsite.chain import apply_chain
from sheetsite.cmdline import run

########################################################
# python2 doesn't have TemporaryDirectory
# replacement begins

import contextlib
import shutil
import tempfile


@contextlib.contextmanager
def TemporaryDirectory():
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath)


# replacement ends
# python2 doesn't have TemporaryDirectory
########################################################


class TestChain(unittest.TestCase):

    def test_json_to_json_cmdline(self):
        with TemporaryDirectory() as temp_dir:
            os.environ['TEST_DIR'] = temp_dir
            run(['--config', 'tests/configs/json_to_json.json', '--cache-dir', temp_dir])

    def test_json_to_json(self):
        with TemporaryDirectory() as temp_dir:
            target = "{}/out.json".format(temp_dir)
            params = {
                "source": {"filename": "tests/configs/things.json"},
                "destination": {"output_file": target}
            }
            apply_chain(params, temp_dir)
            with open(target, 'r') as f:
                data = json.load(f)
            assert len(data["tables"]["countries"]["columns"]) == 2
            assert data["tables"]["countries"]["rows"][1]["code"] == ""

    def test_fill(self):
        with TemporaryDirectory() as temp_dir:
            target = "{}/out.json".format(temp_dir)
            params = {
                "source": {"filename": "tests/configs/fill.json"},
                "flags": {
                    "geocoder": "dummy",
                    "address": {"countries": ["country"]}
                },
                "destination": {"output_file": target}
            }
            apply_chain(params, temp_dir)
            with open(target, 'r') as f:
                data = json.load(f)
            assert data["tables"]["countries"]["rows"][0]["zip"] == "PO-STAL"

    def test_single_to_multiple_add(self):
        with TemporaryDirectory() as temp_dir:
            target = "{}/out.json".format(temp_dir)
            params = {
                "source": {"filename": "tests/configs/things.json"},
                "flags": {
                    "geocoder": "dummy",
                    "address": {"countries": ["country"]},
                    "add": {"countries": ["city", "address"]}
                },
                "destination": {"output_file": target}
            }
            apply_chain(params, temp_dir)
            with open(target, 'r') as f:
                data = json.load(f)
            assert data["tables"]["countries"]["rows"][0]["city"] == "Cityville"
            assert data["tables"]["countries"]["rows"][0]["address"] == "United Kingdom"
            assert data["tables"]["countries"]["rows"][1]["address"] == "United States"

    def test_multiple_to_multiple_add(self):
        with TemporaryDirectory() as temp_dir:
            target = "{}/out.json".format(temp_dir)
            params = {
                "source": {"filename": "tests/configs/things.json"},
                "flags": {
                    "geocoder": "dummy",
                    "address": {"countries": ["code", "country", "Earth"]},
                    "add": {"countries": ["city", "address"]}
                },
                "destination": {"output_file": target}
            }
            apply_chain(params, temp_dir)
            with open(target, 'r') as f:
                data = json.load(f)
            assert data["tables"]["countries"]["rows"][0]["city"] == "Cityville"
            assert data["tables"]["countries"]["rows"][0]["address"] == "uk United Kingdom Earth"

    def test_multirow(self):
        with TemporaryDirectory() as temp_dir:
            target = "{}/out.json".format(temp_dir)
            params = {
                "source": {"filename": "tests/configs/multirow.json"},
                "flags": {
                    "geocoder": "dummy",
                    "group": "web",
                    "address": {"places": ["street", "city", "state", "country"]},
                    "add": {"places": ["lat", "lon", "address"]}
                },
                "destination": {"output_file": target}
            }
            apply_chain(params, temp_dir)
            with open(target, 'r') as f:
                data = json.load(f)
            places = data["tables"]["places"]["rows"]
            self.assertEqual(places[0]["address"], "Test1 Test2")
            self.assertEqual(places[1]["address"], "Test1")
            self.assertEqual(places[2]["address"],
                             "305 Memorial Dr Cambridge Massachusetts United States")
            self.assertEqual(places[3]["address"],
                             "306 Memorial Dr Cambridge Massachusetts United States")

    def test_rename(self):
        with TemporaryDirectory() as temp_dir:
            target = "{}/out.json".format(temp_dir)
            params = {
                "source": {"filename": "tests/configs/multirow.json"},
                "flags": {
                    "geocoder": "dummy",
                    "rename": {"places": {"web": "website"}},
                    "address": {"places": ["street", "city", "state", "country"]},
                    "add": {"places": ["lat", "lon", "address"]}
                },
                "destination": {"output_file": target}
            }
            apply_chain(params, temp_dir)
            with open(target, 'r') as f:
                data = json.load(f)
            places = data["tables"]["places"]["rows"]
            self.assertIn('website', places[0])
            self.assertNotIn('web', places[0])
