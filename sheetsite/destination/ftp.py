import os
import subprocess

def write_destination_ftp(params, state):
    path = state['path']
    output_file = state['output_file']
    sqlite_file = os.path.join(path, 'site.sqlite3')
    subprocess.check_output(['ssformat',
                             'dbi:jsonbook::file={}'.format(output_file),
                             sqlite_file])
    #subprocess.check_output(['wput', '-v', '--binary', '-u', '-nc', 'x.sqlite3', 'ftp://url'])
    return True


