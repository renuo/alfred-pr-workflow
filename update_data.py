#!/usr/local/bin/python

from workflow import Workflow3, web, PasswordNotFound
from workflow.notify import notify


def params(token):
    return dict(access_token=token, format='json')


def merge_results(assignee_prs, reviews_prs):
    assigned_items = assignee_prs.json()['items']
    review_requested_items = reviews_prs.json()['items']
    return list({v['html_url']: v for v in (assigned_items + review_requested_items)}.values())


def get_username(token):
    username_url = 'https://api.github.com/user'
    response = web.get(username_url, params(token))
    return response.json()['login']


def get_pull_requests(username, token):
    search_assignees_url = 'https://api.github.com/search/issues?q=type:pr is:open assignee:%s' % username
    search_reviews_url = 'https://api.github.com/search/issues?q=type:pr is:open review-requested:%s' % username
    response_assignees = web.get(search_assignees_url, params(token))
    response_reviews = web.get(search_reviews_url, params(token))
    response_assignees.raise_for_status()
    response_reviews.raise_for_status()
    return merge_results(response_assignees, response_reviews)


def main(workflow):
    try:
        auth_token = workflow.get_password('ghpr-auth-token')
        username = workflow.cached_data('username', max_age=0)
        if username is None:
            username = get_username(auth_token)
            workflow.cache_data('username', username)
        workflow.cache_data('pull_requests', get_pull_requests(username, auth_token))
        workflow.send_feedback()
    except PasswordNotFound:
        notify('Github PRs', 'Please set the API key first.')
        return 1


if __name__ == u"__main__":
    alfred_workflow = Workflow3()
    alfred_workflow.run(main)
