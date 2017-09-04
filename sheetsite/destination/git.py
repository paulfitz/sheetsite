import os
import shutil
import subprocess


def write_destination_git(destination, state):
    wd = os.getcwd()
    try:
        path = state['path']
        output_file = state['output_file']
        local_repo = os.path.join(path, destination.get('local', 'repo'))
        if not(os.path.exists(local_repo)):
            subprocess.check_output(['git', 'clone', destination['repo'], local_repo])
        os.chdir(local_repo)
        subprocess.check_output(['git', 'pull'])
        os.chdir(wd)
        shutil.copyfile(output_file, os.path.join(local_repo, destination['file']))
        os.chdir(local_repo)
        subprocess.check_output(['git', 'add', destination['file']])
        try:
            subprocess.check_output(['git', 'commit', '-m', 'update from sheetsite'])
            subprocess.check_output(['git', 'push'])
        except subprocess.CalledProcessError:
            print("Commit/push skipped")
    finally:
        os.chdir(wd)
