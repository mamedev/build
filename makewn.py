#!/usr/bin/python
##
## license:BSD-3-Clause
## copyright-holders:Vas Crabb

import argparse
import getpass
import git
import os.path
import pygithub3
import re
import sys
import xml.sax
import xml.sax.handler


class softlist_comparator(object):
    class ErrorHandler(object):
        def __init__(self, **kwargs):
            super(softlist_comparator.ErrorHandler, self).__init__(**kwargs)
            self.errors = 0
            self.warnings = 0

        def error(self, exception):
            self.errors += 1
            sys.stderr.write('error: %s\n' % (exception, ))

        def fatalError(self, exception):
            raise exception

        def warning(self, exception):
            self.warnings += 1
            sys.stderr.write('warning: %s\n' % (exception, ))


    class Categoriser(object):
        def __init__(self, error_handler, **kwargs):
            super(softlist_comparator.Categoriser, self).__init__(**kwargs)

            # handling the XML
            self.error_handler = error_handler
            self.locator = None

            # parse state
            self.in_document = False
            self.in_softlist = False
            self.in_software = False
            self.in_description = False
            self.ignored_depth = 0

            # attributes of current item
            self.softname = None
            self.is_clone = None
            self.is_working = None
            self.description = None

            # output
            self.listname = None

        def startElement(self, name, attrs):
            if not self.in_document:
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Got start of element outside document',
                        None,
                        self.locator))
            elif self.ignored_depth > 0:
                self.ignored_depth += 1
            elif not self.in_softlist:
                if name != 'softwarelist':
                    self.error_handler.fatalError(xml.sax.SAXParseException(
                            'Found unexpected element %s' % (name, ),
                            None,
                            self.locator))
                elif 'name' not in attrs:
                    self.error_handler.fatalError(xml.sax.SAXParseException(
                            'Expected attribute name not found',
                            None,
                            self.locator))
                else:
                    self.in_softlist = True
                    self.listname = attrs['name']
            elif not self.in_software:
                if name != 'software':
                    self.error_handler.fatalError(xml.sax.SAXParseException(
                            'Found unexpected element %s' % (name, ),
                            None,
                            self.locator))
                elif 'name' not in attrs:
                    self.error_handler.fatalError(xml.sax.SAXParseException(
                            'Expected attribute name not found',
                            None,
                            self.locator))
                else:
                    self.in_software = True
                    self.softname = attrs['name']
                    self.is_clone = 'cloneof' in attrs
                    self.is_working = ('supported' not in attrs) or (attrs['supported'] != 'no')
            elif not self.in_description:
                if name == 'description':
                    self.in_description = True
                    self.description = ''
                else:
                    self.ignored_depth = 1
            else:
                self.ignored_depth = 1;

        def endElement(self, name):
            if self.ignored_depth > 0:
                self.ignored_depth -= 1
            elif self.in_description:
                if name != 'description':
                    self.error_handler.fatalError(xml.sax.SAXParseException(
                            'End of element %s does not match start of element description' % (name, ),
                            None,
                            self.locator))
                else:
                    self.in_description = False
            elif self.in_software:
                if name != 'software':
                    self.error_handler.fatalError(xml.sax.SAXParseException(
                            'End of element %s does not match start of element software' % (name, ),
                            None,
                            self.locator))
                else:
                    if self.description is None:
                        self.error_handler.error(xml.sax.SAXParseException(
                                'Expected element description not found',
                                None,
                                self.locator))
                    else:
                        self.handleSoftware(self.softname, self.description, self.is_clone, self.is_working)
                    self.in_software = False
                    self.softname = None
                    self.is_clone = None
                    self.is_working = None
                    self.description = None
            elif self.in_softlist:
                if name != 'softwarelist':
                    self.error_handler.fatalError(xml.sax.SAXParseException(
                            'End of element %s does not match start of element softwarelist' % (name, ),
                            None,
                            self.locator))
                else:
                    self.in_softlist = False
            else:
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Found unexpected end of element %s' % (name, ),
                        None,
                        self.locator))

        def startDocument(self):
            if self.in_document:
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Got start of document inside document',
                        None,
                        self.locator))
            else:
                self.in_document = True

        def endDocument(self):
            if self.in_softlist:
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Got end of document inside softwarelist element',
                        None,
                        self.locator))
            else:
                self.in_document = False

        def setDocumentLocator(self, locator):
            self.locator = locator

        def startPrefixMapping(self, prefix, uri):
            pass

        def endPrefixMapping(self, prefix):
            pass

        def characters(self, content):
            if self.in_description and (self.ignored_depth == 0):
                self.description += content

        def ignorableWhitespace(self, whitespace):
            pass

        def processingInstruction(self, target, data):
            pass


    def __init__(self, output, verbose=False, **kwargs):
        super(softlist_comparator, self).__init__(**kwargs)
        self.output = output
        self.verbose = verbose

    def compare(self, current, baseline):
        error_handler = self.ErrorHandler()
        content_handler = self.Categoriser(error_handler)
        parser = xml.sax.make_parser()
        parser.setErrorHandler(error_handler)
        parser.setContentHandler(content_handler)
        parser.setFeature(xml.sax.handler.feature_external_ges, False)

        old_working = dict()
        old_nonworking = dict()
        old_descriptions = dict()
        if baseline is not None:
            def handle_old_software(shortname, description, is_clone, is_working):
                if self.verbose:
                    sys.stderr.write('item %s (%s) previously %sworking\n' % (shortname, description, '' if is_working else 'not '))
                if is_working: old_working[shortname] = description
                else: old_nonworking[shortname] = description
                old_descriptions[description] = shortname
            content_handler.handleSoftware = handle_old_software
            parser.parse(baseline.data_stream)

        new_working = dict()
        new_nonworking = dict()
        added_working = set()
        added_nonworking = set()
        promoted = set()
        renames = dict()
        def handle_new_software(shortname, description, is_clone, is_working):
            if self.verbose:
                sys.stderr.write('item %s (%s) now %sworking' % (shortname, description, '' if is_working else 'not '))
            if is_working: new_working[shortname] = description
            else: new_nonworking[shortname] = description
            if (shortname in old_working) or (shortname in old_nonworking): old_name = shortname
            elif description in old_descriptions: old_name = old_descriptions[description]
            else: old_name = None
            if (old_name is None) or (old_name in renames):
                if self.verbose:
                    sys.stderr.write(' (added)\n')
                if is_working: added_working.add(description)
                else: added_nonworking.add(description)
            else:
                if old_name != shortname:
                    if self.verbose:
                        sys.stderr.write(' (was %s)\n' % (old_name, ))
                    renames[old_name] = (description, shortname)
                    if old_name in new_working: added_working.add(new_working[old_name])
                    elif old_name in new_nonworking: added_nonworking.add(new_nonworking[old_name])
                if is_working and (old_name not in old_working):
                    if self.verbose:
                        sys.stderr.write(' (promoted)\n')
                    promoted.add(description)
                elif self.verbose:
                    sys.stderr.write('\n')
        content_handler.handleSoftware = handle_new_software
        parser.parse(current.data_stream)
        listname = content_handler.listname

        for shortname in new_working:
            if shortname in old_working: del old_working[shortname]
            elif shortname in old_nonworking: del old_nonworking[shortname]
        for shortname in new_nonworking:
            if shortname in old_working: del old_working[shortname]
            elif shortname in old_nonworking: del old_nonworking[shortname]
        for shortname in renames:
            if shortname in old_working: del old_working[shortname]
            elif shortname in old_nonworking: del old_nonworking[shortname]
        removed = list()
        for shortname, description in old_working.iteritems(): removed.append(description)
        for shortname, description in old_nonworking.iteritems(): removed.append(description)
        removed.sort()

        if renames or removed or added_working or added_nonworking or promoted:
            self.output.write(('%s (%s):\n' % (listname, current.name)).encode('UTF-8'))
            if renames:
                self.output.write('  Renames\n'.encode('UTF-8'))
                for old_name, info in renames.iteritems():
                    self.output.write(('    %s -> %s %s\n' % (old_name, info[1], info[0])).encode('UTF-8'))
            if removed:
                self.output.write('  Removed\n'.encode('UTF-8'))
                for description in removed:
                    self.output.write(('    %s\n' % (description, )).encode('UTF-8'))
            if added_working:
                self.output.write('  Working\n'.encode('UTF-8'))
                for description in sorted(added_working):
                    self.output.write(('    %s\n' % (description, )).encode('UTF-8'))
            if added_nonworking:
                self.output.write('  Non-working\n'.encode('UTF-8'))
                for description in sorted(added_nonworking):
                    self.output.write(('    %s\n' % (description, )).encode('UTF-8'))
            if promoted:
                self.output.write('  Promoted\n'.encode('UTF-8'))
                for description in sorted(promoted):
                    self.output.write(('    %s\n' % (description, )).encode('UTF-8'))
            self.output.write('\n'.encode('UTF-8'))


releasetag_pat = re.compile('^mame0([0-9]+)$')
nowhatsnew_pat = re.compile('.*([[(]n/?w[])].*|[\s,]n/?w$)')
bullet_pat = re.compile('^([-*]\s*)?(.+)$')
credit_pat = re.compile('^.+\s\[.+\]$')
markdown_url_pat = re.compile('\[([^]]+)\]\(([^)])+\)')
newdrivers_pat = re.compile('^new|(game|machine|system|clone)s? promot')
softlist_pat = re.compile('soft(ware)? ?list')
notworking_pat = re.compile('not[_ ]working')
longdash_pat = re.compile('^-{2,}$')

new_working_parents = []
new_promoted_parents = []
new_broken_parents = []
new_working_clones = []
new_promoted_clones = []
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
    if (newdrivers_pat.match(line) is not None) and (softlist_pat.match(line) is None):
        clone = line.find('clone') >= 0
        if line.find('promot') >= 0:
            working = True
            promoted = True
        elif notworking_pat.search(line) is not None:
            working = False
            promoted = False
        else:
            working = True
            promoted = False
        if clone:
            return new_promoted_clones if promoted else new_working_clones if working else new_broken_clones
        else:
            return new_promoted_parents if promoted else new_working_parents if working else new_broken_parents
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
    parser.add_argument('-t', '--token', metavar='<token>', type=str, help='github personal access token')
    parser.add_argument('-o', '--out', metavar='<file>', type=str, help='output file')
    parser.add_argument('-a', '--append', action='store_const', const=True, default=False, help='append to output file')
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False, help='verbose output')
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
    if args.token is not None:
        api = pygithub3.Github(user='mamedev', repo='mame', login=ghuser, token=args.token)
    else:
        api = pygithub3.Github(user='mamedev', repo='mame', login=ghuser, token=getpass.getpass('github personal access token: '))
    tag = get_most_recent_tag(repo)

    placeholders = (
            '0.%s' % (long(releasetag_pat.sub('\\1', tag.name)) + 1, ),
            'MAME Testers Bugs Fixed',
            'New working machines',                 'New working clones' ,
            'Machines promoted to working',         'Clones promoted to working',
            'New machines marked as NOT_WORKING',   'New clones marked as NOT_WORKING',
            'New working software list additions',
            'Software list items promoted to working',
            'New NOT_WORKING software list additions',
            'Translations added or modified')
    for heading in placeholders:
        print_section_heading(stream, heading)
        stream.write('\n\n'.encode('UTF-8'))

    print_source_changes(stream, repo, api, tag)
    print_new_machines(stream, 'New working machines', new_working_parents);
    print_new_machines(stream, 'New working clones', new_working_clones);
    print_new_machines(stream, 'Machines promoted to working', new_promoted_parents);
    print_new_machines(stream, 'Clones promoted to working', new_promoted_clones);
    print_new_machines(stream, 'New machines marked as NOT_WORKING', new_broken_parents);
    print_new_machines(stream, 'New clones marked as NOT_WORKING', new_broken_clones);

    comp = softlist_comparator(stream, args.verbose)
    current = repo.commit('release0%ld' % (long(releasetag_pat.sub('\\1', tag.name)) + 1, )).tree['hash']
    previous = repo.commit(tag).tree['hash']
    for obj in current:
        if obj.type == 'blob':
            basename, extension = os.path.splitext(obj.name)
            if extension == '.xml':
                if args.verbose:
                    sys.stderr.write('checking software list %s\n' % (obj.name, ))
                try:
                    baseline = previous / obj.name
                except KeyError:
                    baseline = None
                if obj != baseline:
                    try:
                        comp.compare(obj, baseline)
                    except xml.sax.SAXException as err:
                        sys.stderr.write('error processing software list %s: %s\n' % (obj.name, err))
                elif args.verbose:
                    sys.stderr.write('no changes since previous release\n')
