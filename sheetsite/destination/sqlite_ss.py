import os
import subprocess

def write_destination_sqlite(params, state):
    path = state['path']
    output_file_prev = state['output_file']
    output_file_next = params['output_file']
    subprocess.check_output(['ssformat',
                             'dbi:jsonbook::file={}'.format(output_file_prev),
                             output_file_next])
    state['output_file'] = output_file_next
    return True
