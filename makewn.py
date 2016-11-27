#!/usr/bin/python
##
## license:BSD-3-Clause
## copyright-holders:Vas Crabb

import argparse
import getpass
import git
import pygithub3
import re
import sys


releasetag_pat = re.compile('^mame0([0-9]+)$')
nowhatsnew_pat = re.compile('.*([[(]n/?w[])].*|[\s,]n/?w$)')
bullet_pat = re.compile('^([-*]\s*)?(.+)$')
credit_pat = re.compile('^.+\s\[.+\]$')
markdown_url_pat = re.compile('\[([^]]+)\]\(([^)])+\)')
softlist_pat = re.compile('soft(ware)? ?list')
notworking_pat = re.compile('not[_ ]working')
longdash_pat = re.compile('^-{2,}$')

new_working_parents = []
new_broken_parents = []
new_working_clones = []
new_broken_clones = []


def print_wrapped(stream, paragraph, level):
    wrapcol = 132
    if level == -1:
        prefix = ''
        indent = '  '
    elif level == 0:
        prefix = '-'
        indent = ' '
    elif level == 1:
        prefix = ' * '
        indent = '    '
    else:
        prefix = '   - '
        indent = '      '
    if nowhatsnew_pat.match(paragraph) is None:
        while paragraph:
            if (len(prefix) + len(paragraph)) > wrapcol:
                pos = paragraph.rfind(' ', 0, wrapcol + 1 - len(prefix))
                if pos < 0:
                    pos = paragraph.find(' ', wrapcol + 1 - len(prefix))
                if pos >= 0:
                    if paragraph[-1] == ']':
                        opening = paragraph.rfind(' [')
                        if (opening >= 0) and (opening < pos):
                            pos = opening
                    line = paragraph[0:pos].strip()
                    paragraph = paragraph[pos:].strip()
            else:
                line = paragraph
                paragraph = ''
            stream.write(('%s%s\n' % (prefix, line)).encode('UTF-8'))
            prefix = indent


def format_paragraph(stream, paragraph, level, author, first):
    if first and (credit_pat.match(paragraph) is None):
        paragraph = '%s [%s]' % (paragraph, author)
    print_wrapped(stream, paragraph, level)


def append_line(paragraph, line):
    if paragraph:
        return '%s %s' % (paragraph, line)
    else:
        return line


def check_new_machines(line):
    line = line.lower()
    if line.startswith('new') and (softlist_pat.match(line) is None):
        clone = line.find('clone') >= 0
        if notworking_pat.match(line) is not None:
            working = line.find('promot') >= 0
        else:
            working = True
        if clone:
            return new_working_clones if working else new_broken_clones
        else:
            return new_working_parents if working else new_broken_parents
    else:
        return None


def format_entry(stream, message, author, checkmachines):
    machines = None
    first = True
    paragraph = ''
    level = 0
    bullet = ''
    for line in message.splitlines():
        line = line.strip().replace('\t', ' ')
        if not line:
            if paragraph:
                machines = None
                if first and (nowhatsnew_pat.match(paragraph) is not None):
                    return
                format_paragraph(stream, paragraph, level, author, first)
                paragraph = ''
                first = False
        elif machines is not None:
            paragraph = ''
            temp = check_new_machines(line)
            if temp is not None:
                machines = temp
            elif longdash_pat.match(line) is None:
                if credit_pat.match(line) is None:
                    machines.append('%s [%s]' % (line, author))
                else:
                    machines.append(line)
        elif (line[0] == '-') or (line[0] == '*'):
            if paragraph:
                if first and (nowhatsnew_pat.match(paragraph) is not None):
                    return
                format_paragraph(stream, paragraph, level, author, first)
                paragraph = ''
                first = False
            if not bullet:
                level = 1
            elif bullet != line[0]:
                level = 1 if level == 2 else 2
            bullet = line[0]
            line = bullet_pat.sub('\\2', line)
            paragraph = append_line(paragraph, line)
        else:
            if checkmachines:
                machines = check_new_machines(line)
            if machines:
                if paragraph:
                    if nowhatsnew_pat.match(paragraph) is None:
                        format_paragraph(stream, paragraph, level, author, first)
                        first = False
                    paragraph = ''
                paragraph = append_line(paragraph, line)
            else:
                if not paragraph:
                    level = 0 if first else 1
                bullet = ''
                paragraph = append_line(paragraph, line)
    if paragraph:
        if first and (nowhatsnew_pat.match(paragraph) is not None):
            return
        format_paragraph(stream, paragraph, level, author, first)
        paragraph = ''
        first = False
    if not first:
        stream.write('\n'.encode('UTF-8'))


def format_commit(stream, commit):
    author = commit.author.name
    if not author:
        author = commit.author.email
    format_entry(stream, commit.message, author, True)


def print_log(stream, repo, revisions):
    commits = repo.iter_commits(revisions, reverse=True)
    for commit in commits:
        if len(commit.parents) == 1:
            format_commit(stream, commit)


def get_most_recent_tag(repo):
    result = None
    best = 0
    for tag in repo.tags:
        match = releasetag_pat.match(tag.name)
        if match is not None:
            num = long(match.group(1))
            if num > best:
                result = tag
    return result


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


def print_fresh_pull_requests(api, stream, commit):
    for pr in fresher_pull_requests(api, commit):
        if pr.title and (pr.title[-1] == unichr(0x2026)) and pr.body and (pr.body[0] == unichr(0x2026)):
            message = pr.title[:-1] + pr.body[1:]
        elif pr.body:
            message = '%s\n%s' % (pr.title, pr.body)
        else:
            message = pr.title
        message = markdown_url_pat.sub('\\1', message)
        format_entry(stream, message, pr.user['login'], True)


def print_section_heading(stream, heading):
    stream.write(('%s\n%s\n' % (heading, '-' * len(heading))).encode('UTF-8'))


def print_source_changes(stream, repo, api, tag):
    print_section_heading(stream, 'Source Changes')
    print_log(stream, repo, '%s..release0%ld' % (tag.name, (long(releasetag_pat.sub('\\1', tag.name)) + 1)))
    print_fresh_pull_requests(api, stream, api.git_data.commits.get(tag.commit.hexsha))
    stream.write('\n'.encode('UTF-8'))


def print_new_machines(stream, title, machines):
    if machines:
        print_section_heading(stream, title)
        for machine in machines:
            print_wrapped(stream, bullet_pat.sub('\\2', machine), -1)
        stream.write('\n\n'.encode('UTF-8'))


def parse_args():
    parser = argparse.ArgumentParser(description='Write preliminary whatsnew.')
    parser.add_argument('-c', '--clone', metavar='<path>', type=str, help='local repository clone')
    parser.add_argument('-u', '--user', metavar='<username>', type=str, help='github username')
    parser.add_argument('-o', '--out', metavar='<file>', type=str, help='output file')
    parser.add_argument('-a', '--append', action='store_const', const=True, default=False, help='append to output file')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.user is not None:
        ghuser = args.user
    else:
        ghuser = raw_input('github username: ')
    if args.out is not None:
        stream = open(args.out, 'a' if args.append else 'w')
    else:
        stream = sys.stdout

    repo = git.Repo(args.clone if args.clone is not None else '.')
    api = pygithub3.Github(user='mamedev', repo='mame', login=ghuser, password=getpass.getpass('github password: '))
    tag = get_most_recent_tag(repo)

    print_section_heading(stream, '0.%s' % (long(releasetag_pat.sub('\\1', tag.name)) + 1))
    stream.write('\n\n'.encode('UTF-8'))

    print_section_heading(stream, 'MAMETesters Bugs Fixed')
    stream.write('\n\n'.encode('UTF-8'))

    print_source_changes(stream, repo, api, tag)
    print_new_machines(stream, 'New machines added or promoted from NOT_WORKING status', new_working_parents);
    print_new_machines(stream, 'New clones added or promoted from NOT_WORKING status', new_working_clones);
    print_new_machines(stream, 'New machines marked as NOT_WORKING', new_broken_parents);
    print_new_machines(stream, 'New clones marked as NOT_WORKING', new_broken_clones);

    print_section_heading(stream, 'New WORKING software list additions')
    stream.write('\n\n'.encode('UTF-8'))

    print_section_heading(stream, 'New NOT_WORKING software list additions')
    stream.write('\n\n'.encode('UTF-8'))

    print_section_heading(stream, 'Translations added or modified')
    stream.write('\n\n'.encode('UTF-8')
