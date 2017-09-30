from sheetsite.chain import apply_chain, compute_diff
from sheetsite.site_queue import app


@app.task
def update_site(params, path, site, name):

    source = site['source']
    destination = site['destination']

    site_params = {
        'name': params.get('title', None),
        'who': params.get('who', None),
        'sheet_link': source.get('link', None),
        'site_link': destination.get('link', None),
        'no_notify': params['no_notify']
    }

    files = apply_chain(site, path)
    diff_html, diff_text = compute_diff(files, format='both')

    from sheetsite.tasks.notify import notify_all
    notify_all.delay(name=name,
                     site_params=site_params,
                     diff_html=diff_html,
                     diff_text=diff_text)
    return True


