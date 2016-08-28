#!/usr/bin/python
##
## license:BSD-3-Clause
## copyright-holders:Vas Crabb

import argparse
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
    lineclean_pat = re.compile('^(\w*[-*])?\w*(.*)$')
    commit = get_latest_tagged_commit(api)
    for pr in fresher_pull_requests(api, commit):
        if nowhatsnew_pat.match(pr.title) is None:
            stream.write(('-%s [%s]\n' % (lineclean_pat.sub('\\2', pr.title), pr.user['login'])).encode('UTF-8'))
            for line in pr.body.splitlines():
                line = lineclean_pat.sub('\\2', line)
                if line != '':
                    stream.write(('  * %s\n' % (line)).encode('UTF-8'))
            stream.write('\n'.encode('UTF-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Retrieve merged pull requests.')
    parser.add_argument('-u', '--user', metavar="<username>", type=str, help='github username')
    parser.add_argument('-o', '--out', metavar='<file>', type=str, help='output file')
    parser.add_argument('-a', '--append', action='store_const', const=True, default=False, help='append to output file')
    args = parser.parse_args()

    if args.user is not None:
        ghuser = args.user
    else:
        ghuser = raw_input('github username: ')
    api = pygithub3.Github(user='mamedev', repo='mame', login=ghuser, password=getpass.getpass('github password: '))

    if args.out is not None:
        stream = open(args.out, 'a' if args.append else 'w')
    else:
        stream = sys.stdout

    with stream:
        print_fresh_pull_requests(api, stream)
