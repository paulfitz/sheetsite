from collections import OrderedDict
import json
import os
import six
import yaml


# borrowed code to load yaml dicts as ordered
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def expand(x):
    return os.path.expandvars(x)


def expand_all(o):
    if type(o) == dict:
        return dict([[k, expand_all(v)] for k, v in o.items()])
    if type(o) == list:
        return [expand_all(x) for x in o]
    if isinstance(o, six.string_types):
        return expand(o)
    return o


def load_config(config_file):
    with open(config_file, 'r') as config:
        _, ext = os.path.splitext(config_file)
        ext = ext.lower()
        if ext == '.yml' or ext == '.yaml':
            import yaml
            params = ordered_load(config, yaml.SafeLoader)
        else:
            params = json.load(config)
        params = expand_all(params)  # should make this optional
    return params
