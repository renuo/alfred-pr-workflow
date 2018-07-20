#!/usr/local/bin/python
import os
import re
import sys
from datetime import datetime

from workflow import Workflow3, ICON_INFO, PasswordNotFound, ICON_WARNING
from workflow.background import run_in_background, is_running


def parse_time(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M')


def parse_project_from_url(url):
    matches = re.search('https:\/\/github.com\/([a-zA-Z0-9/_\-]+)\/pull', url)
    return matches.group(1) if matches else ''


def merge_results(assignee_prs, reviews_prs):
    assigned_items = assignee_prs.json()['items']
    review_requested_items = reviews_prs.json()['items']
    return {v['html_url']: v for v in (assigned_items + review_requested_items)}.values()


def main(workflow):
    try:
        auth_token = workflow.get_password('ghpr-auth-token')
    except PasswordNotFound:
        workflow.add_item('No API key set',
                          'Please use ghpr-auth to set your GitHub personal token.',
                          arg='https://github.com/settings/tokens/new',
                          valid=False,
                          icon=ICON_WARNING)
        workflow.send_feedback()
        return 1

    cache_max_age = int(os.getenv('CACHE_MAX_AGE') or '60')
    if not workflow.cached_data_fresh('pull_requests', max_age=cache_max_age):
        run_in_background('update', ['/usr/bin/python', workflow.workflowfile('update_data.py'), auth_token])

    data = workflow.cached_data('pull_requests', max_age=0)
    if data:
        for pr in data:
            workflow.add_item(pr['title'],
                              '%s by %s, %s' % (parse_project_from_url(pr['html_url']), pr['user']['login'],
                                                parse_time(pr['updated_at'])), valid=True, arg=pr['html_url'])
    if is_running('update'):
        workflow.rerun = 0.5
        workflow.add_item('Fetching pull requests...', icon=ICON_INFO)

    workflow.send_feedback()


if __name__ == u"__main__":
    alfred_workflow = Workflow3()
    sys.exit(alfred_workflow.run(main))
