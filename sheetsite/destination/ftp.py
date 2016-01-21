import os
import subprocess

def write_destination_ftp(params, state):
    output_file = state['output_file']
    url = params['url']
    cmd = ['wput', '-v', '--binary', '-u', '-nc', output_file, url]
    print(' '.join(cmd))
    out = subprocess.check_output(cmd)
    print("ftp: {}".format(out))
    return True
