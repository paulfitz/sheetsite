from sheetsite.source.google import read_source_google

def read_source(params):

    readers = {
        'google-sheets': read_source_google
    }

    if 'name' not in params:
        return IOError('source not specified')

    name = params['name']

    if name not in readers:
        return IOError('source not recognized: {}'.format(name))

    return readers[name](params)


