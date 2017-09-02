import json
import os


def expand(x):
    return os.path.expandvars(x)


def expand_all(o):
    if type(o) == dict:
        return dict([[k, expand_all(v)] for k, v in o.items()])
    if type(o) == list:
        return [expand_all(x) for x in o]
    if type(o) == str or type(o) == unicode:
        return expand(o)
    return o


def load_config(config_file):
    with open(config_file, 'r') as config:
        _, ext = os.path.splitext(config_file)
        ext = ext.lower()
        if ext == '.yml' or ext == '.yaml':
            import yaml
            params = yaml.safe_load(config)
        else:
            params = json.load(config)
        params = expand_all(params)  # should make this optional
    return params
