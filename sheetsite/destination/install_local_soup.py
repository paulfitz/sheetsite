import subprocess

# Hey this is embarrassing I'll remove it soon I promise.
# I mean, maybe.  Or I'll leave it malingering for years.


def apply(params, state):
    subprocess.check_output(["cp",
                             state['sqlite_file'],
                             "/srv/git/datacommons_manitoba/production.sqlite3"])
    ok = False
    for i in range(0, 4):
        try:
            subprocess.check_output(["/srv/git/datacommons_manitoba/rebuild.sh"])
            ok = True
            break
        except subprocess.CalledProcessError:
            pass

    if not ok:
        raise subprocess.CalledProcessError("rebuild sadness")

    return True
