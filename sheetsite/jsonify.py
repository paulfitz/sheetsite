from datetime import date, datetime
import json


def json_serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Cannot deserialize %s" % type(obj))


def dump(*args, **kwargs):
    kwargs['default'] = json_serialize
    json.dump(*args, **kwargs)

def dumps(*args, **kwargs):
    kwargs['default'] = json_serialize
    return json.dumps(*args, **kwargs)
