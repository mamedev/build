#!/usr/bin/python
##
## license:BSD-3-Clause
## copyright-holders:Vas Crabb

import getpass
import pygithub3
import re
import sys


def get_latest_tagged_commit(api):
    pat = re.compile('^mame0[0-9]+$')
    for page in api.repos.list_tags():
        for tag in page:
            if pat.match(tag.name) is not None:
                return api.git_data.commits.get(tag.commit.sha)


def fresher_pull_requests(api, commit):
    for page in api.pull_requests.list(state='closed'):
        for pr in page:
            if (pr.merged_at is not None) and (pr.merged_at > commit.committer.date):
                yield pr


def print_fresh_pull_requests(api, stream):
    nowhatsnew_pat = re.compile('.*[[(]nw[])].*')
    lineclean_pat = re.compile('^(\w*[-*]\w*)?(.*)$')
    commit = get_latest_tagged_commit(api)
    for pr in fresher_pull_requests(api, commit):
        if nowhatsnew_pat.match(pr.title) is None:
            stream.write(('-%s [%s]\n' % (lineclean_pat.sub('\\2', pr.title), pr.user['login'])).encode('UTF-8'))
            for line in pr.body.splitlines():
                line = lineclean_pat.sub('\\2', line)
                if line != '':
                    stream.write(('  * %s\n' % (line)).encode('UTF-8'))
            stream.write('\n'.encode('UTF-8'))


ghuser = 'get_github_user_from_somewhere'
api = pygithub3.Github(user='mamedev', repo='mame', login=ghuser, password=getpass.getpass('github password: '))
print_fresh_pull_requests(api, sys.stdout)
