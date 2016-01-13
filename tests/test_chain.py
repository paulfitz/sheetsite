import json
from tempfile import TemporaryDirectory
from sheetsite.chain import apply_chain
from sheetsite.cmdline import run

def test_json_to_json_cmdline():
    with TemporaryDirectory() as temp_dir:
        def tweak(param):
            param["destination"]["output_file"] = "{}/out.json".format(temp_dir)
        run(['--config', 'tests/configs/json_to_json.json', '--cache-dir', temp_dir],
            tweak)


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
