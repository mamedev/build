#!/usr/bin/python3
##
## license:BSD-3-Clause
## copyright-holders:Vas Crabb

import argparse
import codecs
import getpass
import git
import io
import os.path
import re
import sys
import xml.sax
import xml.sax.handler


try:
    import github
except ImportError:
    try:
        import github3
    except ImportError:
        import pygithub3

if 'github' in locals():
    class GithubWrapper:
        @staticmethod
        def pull_request_username(pr):
            return pr.user.login

        def __init__(self, owner, repo, user, password=None, token=None, **kwargs):
            super().__init__(**kwargs)
            if token is not None:
                self.session = github.Github(token)
            elif password is not None:
                self.session = github.Github(user, password)
            else:
                self.session = github.Github(user)
            self.repo = self.session.get_repo(owner + '/' + repo)

        def fresher_pull_requests(self, commits):
            for pr in self.repo.get_pulls(state='closed', sort='created', direction='asc'):
                if (pr.merged_at is not None) and (pr.merge_commit_sha in commits):
                    yield pr


elif 'github3' in locals():
    class GithubWrapper:
        @staticmethod
        def pull_request_username(pr):
            return pr.user.login

        def __init__(self, owner, repo, user, password=None, token=None, **kwargs):
            super().__init__(**kwargs)
            if (token is None) and (password is None):
                self.session = github3.GitHub(user)
            elif token is None:
                self.session = github3.GitHub(user, password)
            elif password is None:
                self.session = github3.GitHub(user, token=token)
            else:
                self.session = github3.GitHub(user, password, token=token)
            self.repo = self.session.repository(owner, repo)

        def fresher_pull_requests(self, commits):
            for pr in self.repo.pull_requests(state='closed', sort='created', direction='asc'):
                if (pr.merged_at is not None) and (pr.merge_commit_sha in commits):
                    yield pr

elif 'pygithub3' in locals():
    class GithubWrapper:
        @staticmethod
        def pull_request_username(pr):
            return pr.user['login']

        def __init__(self, owner, repo, user, password=None, token=None, **kwargs):
            super().__init__(**kwargs)
            if (token is None) and (password is None):
                self.api = pygithub3.Github(user=owner, repo=repo, login=user)
            elif token is None:
                self.api = pygithub3.Github(user=owner, repo=repo, login=user, password=password)
            elif password is None:
                self.api = pygithub3.Github(user=owner, repo=repo, login=user, token=token)
            else:
                self.api = pygithub3.Github(user=owner, repo=repo, login=user, password=password, token=token)

        def fresher_pull_requests(self, sha):
            date = self.api.git_data.commits.get(sha).committer.date
            for page in self.api.pull_requests.list(state='closed'):
                for pr in page:
                    if (pr.merged_at is not None) and (pr.merged_at > date):
                        yield pr


class Options:
    RELEASETAG = re.compile('^mame0([0-9]+)$')
    VERSIONPART = re.compile('^[^0-9]+0([1-9][0-9]*)([^0-9]*)$')

    def fail(self, message):
        sys.stderr.write('%s: error: %s\n' % (os.path.basename(sys.argv[0]), message))
        sys.exit(1)

    def find_revision(self, spec, name, verbose):
        try:
            result = self.repository.references[spec]
            if verbose:
                sys.stderr.write('using %s %s\n' % (name, result.name))
            return result
        except IndexError:
            suffix = re.compile('^[^/]+/' + re.escape(spec))
            for ref in self.repository.references:
                if suffix.match(ref.name):
                    if verbose:
                        sys.stderr.write('using %s %s\n' % (name, ref.name))
                    return ref
            try:
                result = self.repository.commit(spec)
            except:
                self.fail('%s %s not found in repository' % (name, spec))
            if verbose:
                sys.stderr.write('using %s %s\n' % (name, result.name_rev))
            return result

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # parse command line
        parser = argparse.ArgumentParser(description='Write preliminary whatsnew.')
        parser.add_argument('-c', '--clone', metavar='<path>', type=str, default='.', help='local repository clone')
        parser.add_argument('-r', '--release', metavar='<release>', type=str, help='previous release revision')
        parser.add_argument('-b', '--branch', metavar='<candidate>', type=str, help='current release candidate revision')
        parser.add_argument('-u', '--user', metavar='<username>', type=str, help='github username')
        parser.add_argument('-t', '--token', metavar='<token>', type=str, help='github personal access token')
        parser.add_argument('-o', '--out', metavar='<file>', type=str, help='output file')
        parser.add_argument('-w', '--wrap', metavar='<column>', type=int, default=132, help='wrap width')
        parser.add_argument('-a', '--append', action='store_const', const=True, default=False, help='append to output file')
        parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False, help='verbose output')
        parser.add_argument('commit', nargs='*', help='scrape specific commits')
        arguments = parser.parse_args()

        # copy simple arguments
        self.wrap = arguments.wrap
        self.verbose = arguments.verbose
        self.commits = arguments.commit

        # it makes no sense to specify baseline/candidate with specific commits
        if ((arguments.release is not None) or (arguments.branch is not None)) and arguments.commit:
            self.fail('arguments -r/--release and -b/--branch: not allowed with specific commits')

        # make sure the wrap width isn't ridiculously narrow
        if arguments.wrap < 40:
            self.fail('argument -w/--wrap: must be no less than 40 columns')

        # open output file or wrap standard output with an encoder if necessary
        if arguments.out is not None:
            self.output = io.open(arguments.out, 'a' if arguments.append else 'w', encoding='utf-8')
        elif sys.stdout.encoding is None:
            self.output = codecs.getwriter('utf-8')(sys.stdout)
        else:
            self.output = sys.stdout

        # open git repository
        try:
            self.repository = git.Repo(arguments.clone)
            if arguments.verbose:
                sys.stderr.write('using git repository %s\n' % (self.repository.working_dir, ))
        except git.exc.InvalidGitRepositoryError as err:
            if arguments.clone == err.args[0]:
                self.fail('%s is not a valid git repository or working tree' % (arguments.clone, ))
            else:
                self.fail('%s (%s) is not a valid git repository or working tree' % (arguments.clone, err.args[0]))
        except git.exc.NoSuchPathError as err:
            if arguments.clone == err.args[0]:
                self.fail('git repository %s not found' % (arguments.clone, ))
            else:
                self.fail('git repository %s (%s) not found' % (arguments.clone, err.args[0]))

        # this stuff is not used when specific commits are requested
        if not arguments.commit:
            # find baseline release if specified
            if arguments.release is not None:
                self.release = self.find_revision(arguments.release, 'baseline release', arguments.verbose)

            # find release candidate if specified
            if arguments.branch is not None:
                self.candidate = self.find_revision(arguments.branch, 'release candidate', arguments.verbose)

            # find most recent release tag if baseline was not specified
            if arguments.release is None:
                best = 0
                for tag in self.repository.tags:
                    match = self.RELEASETAG.match(tag.name)
                    if match is not None:
                        num = int(match.group(1))
                        if num > best:
                            self.release = tag
                            best = num
                if best <= 0:
                    self.fail('could not find a tagged release in repository')
                if arguments.verbose:
                    sys.stderr.write('found tagged release %s for baseline\n' % self.release.name)

            # guess release candidate branch name if it wasn't specified
            if arguments.branch is None:
                version = self.VERSIONPART.match(self.release.name) if hasattr(self.release, 'name') else None
                if not version:
                    self.fail('could not guess release candidate branch name')
                self.candidate = self.find_revision('release0%ld' % (int(version.group(1)) + 1, ), 'release candidate', arguments.verbose)

            # come up with a title
            version = self.VERSIONPART.match(self.candidate.name) if hasattr(self.candidate, 'name') else None
            if version:
                self.title = '0.%s%s' % version.group(1, 2)
            else:
                version = self.VERSIONPART.match(self.release.name) if hasattr(self.release, 'name') else None
                if version:
                    self.title = '0.%ld' % (int(version.group(1)) + 1, )
                else:
                    self.title = self.candidate.name if hasattr(self.candidate, 'name') else self.candidate.name_rev

            # ensure the baseline and release candidate are commit objects
            self.release = self.repository.commit(self.release)
            self.candidate = self.repository.commit(self.candidate)

            # prompt for GitHub credentials if necessary and open API
            if arguments.user is not None:
                ghuser = arguments.user
            else:
                ghuser = raw_input('github username: ')
            if arguments.token is not None:
                self.api = GithubWrapper('mamedev', 'mame', ghuser, token=arguments.token)
            else:
                self.api = GithubWrapper('mamedev', 'mame', ghuser, token=getpass.getpass('github personal access token: '))


class SoftlistComparator:
    class OStreamWrapper:
        def __init__(self, stream, **kwargs):
            super().__init__(**kwargs)
            self.stream = stream

        def __getattr__(self, attr):
            return getattr(self if attr in self.__dict__ else self.stream, attr)

        def close(self):
            pass


    class ErrorHandler:
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
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


    class Categoriser:
        def __init__(self, error_handler, **kwargs):
            super().__init__(**kwargs)

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
                if name == 'notes':
                    self.ignored_depth = 1
                elif name != 'software':
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
        super().__init__(**kwargs)
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
            filename = baseline.name
            baseline = baseline.data_stream
            if not hasattr(baseline, 'close'):
                baseline = self.OStreamWrapper(baseline)
            parser.parse(baseline)
            del baseline
            listname = content_handler.listname

        new_working = dict()
        new_nonworking = dict()
        added_working = set()
        added_nonworking = set()
        promoted = set()
        renames = dict()
        if current is not None:
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
            filename = current.name
            current = current.data_stream
            if not hasattr(current, 'close'):
                current = self.OStreamWrapper(current)
            parser.parse(current)
            del current
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
        for shortname, description in old_working.items(): removed.append(description)
        for shortname, description in old_nonworking.items(): removed.append(description)
        removed.sort()

        if renames or removed or added_working or added_nonworking or promoted:
            self.output.write(u'%s (%s):\n' % (listname, filename))
            if renames:
                self.output.write(u'  Renames\n')
                for old_name, info in renames.items():
                    self.output.write(u'    %s -> %s %s\n' % (old_name, info[1], info[0]))
            if removed:
                self.output.write(u'  Removed\n')
                for description in removed:
                    self.output.write(u'    %s\n' % (description, ))
            if added_working:
                self.output.write(u'  Working\n')
                for description in sorted(added_working):
                    self.output.write(u'    %s\n' % (description, ))
            if added_nonworking:
                self.output.write(u'  Non-working\n')
                for description in sorted(added_nonworking):
                    self.output.write(u'    %s\n' % (description, ))
            if promoted:
                self.output.write(u'  Promoted\n')
                for description in sorted(promoted):
                    self.output.write(u'    %s\n' % (description, ))
            self.output.write(u'\n')


class LogScraper:
    LEADINGSPACE = re.compile('^(\s*)(.*)$')
    DIVIDERLINE = re.compile('^---+$')
    CREDITED = re.compile('^.+\s\[.+\]$')

    class Formatter:
        def __init__(self, stream, wrapcol, listcallback, author, **kwargs):
            super().__init__(**kwargs)
            self.stream = stream
            self.wrapcol = wrapcol
            self.listcallback = listcallback
            self.author = author
            self.paragraph = ''
            self.first = True
            self.blank = False
            self.level = 0
            self.bullets = list()
            self.listname = None
            self.listitems = False

        def flush_paragraph(self):
            if self.paragraph:
                if (self.level == 0) and not LogScraper.CREDITED.match(self.paragraph):
                    self.paragraph += ' ['
                    self.paragraph += self.author
                    self.paragraph += ']'
                if self.stream is not None:
                    if not self.first and (self.level == 0):
                        self.stream.write(u'\n')
                    print_wrapped(self.stream, self.wrapcol, self.paragraph, self.level)
                self.paragraph = ''
                self.first = False
                self.blank = False

        def append_line(self, line):
            if self.paragraph:
                self.paragraph += ' '
            self.paragraph += line

        def get_bullet_increment(self, indent, bullet):
            indent = len(indent)
            if not self.bullets:
                if not self.first:
                    self.level += 1
                self.bullets.append((bullet, indent))
            elif bullet == self.bullets[-1][0]:
                if indent < self.bullets[-1][1]:
                    for i in range(len(self.bullets)):
                        if (bullet == self.bullets[i][0]) and (indent <= self.bullets[i][1]):
                            self.level -= len(self.bullets) - i - 1
                            del self.bullets[(i + 1):]
                            break
            elif indent > self.bullets[-1][1]:
                self.level += 1
                self.bullets.append((bullet, indent))
            else:
                for i in range(len(self.bullets)):
                    if (bullet == self.bullets[i][0]) and (indent <= self.bullets[i][1]):
                        self.level -= len(self.bullets) - i - 1
                        del self.bullets[(i + 1):]
                        break
                else:
                    self.level += 1
                    self.bullets.append((bullet, indent))

        def process_line(self, line):
            indent, line = LogScraper.LEADINGSPACE.match(line.rstrip().replace('\t', ' ')).groups()
            if not line:
                if self.listname is None:
                    self.blank = True
                elif self.listitems:
                    self.listname = None
            elif LogScraper.DIVIDERLINE.match(line) and self.paragraph:
                if self.stream is not None:
                    if not self.first:
                        self.stream.write(u'\n')
                    wrap = wrap_paragraph(self.stream, self.paragraph, self.wrapcol, '', '  ')
                    self.stream.write('%s\n' % (u'-' * wrap, ))
                self.listname = self.paragraph
                self.paragraph = ''
                self.first = True
                self.blank = False
                self.level = 0
                self.bullets = list()
            elif self.listname is not None:
                if not LogScraper.CREDITED.match(line):
                    line = u'%s [%s]' % (line, self.author)
                self.listcallback(self.listname, line)
                if self.stream is not None:
                    if not self.listitems:
                        self.listitems = True
                    wrap_paragraph(self.stream, line, self.wrapcol, '', '  ')
            elif (line[0] == '-') or (line[0] == '*'):
                self.flush_paragraph()
                self.blank = False
                if self.listitems:
                    if self.stream is not None:
                        self.stream.write(u'\n')
                    self.listitems = False
                bullet = line[0]
                line = line[1:].lstrip()
                self.get_bullet_increment(indent, bullet)
                self.append_line(line)
            else:
                if self.blank:
                    self.flush_paragraph()
                    self.blank = False
                if self.listitems:
                    if self.stream is not None:
                        self.stream.write(u'\n')
                    self.listitems = False
                if not self.first and not self.paragraph:
                    if not self.bullets:
                        self.level = 1
                    else:
                        self.get_bullet_increment('', '')
                self.append_line(line)

        def finalise(self):
            self.flush_paragraph()
            if self.stream is not None:
                self.stream.write(u'\n')

    def __init__(self, stream, wrapcol, listcallback, **kwargs):
        super().__init__(**kwargs)
        self.stream = stream
        self.wrapcol = wrapcol
        self.listcallback = listcallback if listcallback is not None else lambda title, entry: None

    def process_commit(self, commit):
        author = commit.author.name
        if not author:
            author = commit.author.email

        fmt = self.Formatter(self.stream if len(commit.parents) == 1 else None, self.wrapcol, self.listcallback, author)
        for line in commit.message.splitlines():
            fmt.process_line(line)
        fmt.finalise()


nowhatsnew_pat = re.compile('.*([[(]n/?w[])].*|[\s,]n/?w$)')
bullet_pat = re.compile('^([-*]\s*)?(.+)$')
credit_pat = re.compile('^(.+)\s+\[(.+)\]$')
markdown_url_pat = re.compile('\[([^]]+)\]\(([^)])+\)')
newdrivers_pat = re.compile('^new|(game|machine|system|clone)s? promot')
softlist_pat = re.compile('soft(ware)? ?list')
notworking_pat = re.compile('not[_ ]working')

new_working_parents = []
new_promoted_parents = []
new_broken_parents = []
new_working_clones = []
new_promoted_clones = []
new_broken_clones = []


def wrap_paragraph(stream, paragraph, wrapcol, prefix, indent):
    maxlen = 0
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
                line = paragraph[0:pos].rstrip()
                paragraph = paragraph[pos:].strip()
            else:
                line = paragraph
                paragraph = ''
        else:
            line = paragraph
            paragraph = ''
        maxlen = max(len(prefix) + len(line), maxlen)
        stream.write(u'%s%s\n' % (prefix, line))
        prefix = indent
    return maxlen


def print_wrapped(stream, wrapcol, paragraph, level):
    if level == -1:
        prefix = ''
        indent = '  '
    elif level == 0:
        prefix = '-'
        indent = ' '
    else:
        indent = ' ' * ((level * 2) - 1)
        prefix = indent + ('* ' if level % 2 else '- ')
        indent += '   '
    return wrap_paragraph(stream, paragraph, wrapcol, prefix, indent)


def print_section_heading(stream, heading):
    stream.write(u'%s\n%s\n' % (heading, '-' * len(heading)))


def print_fresh_pull_requests(stream, wrapcol, repo, api, previous, current):
    print_section_heading(stream, u'Merged pull requests')
    commits = frozenset(repo.git.rev_list(current.hexsha, '^' + previous.hexsha).splitlines())
    for pr in api.fresher_pull_requests(commits):
        lines = markdown_url_pat.sub('\\1', pr.body).splitlines() if pr.body else ()
        title = u'%d: %s' % (pr.number, pr.title)
        if (title[-1] == chr(0x2026)) and pr.body and lines and lines[0] and (lines[0][0] == chr(0x2026)):
            title = title[:-1] + lines[0][1:]
            lines = lines[1:]
        title += u' [%s]' % (api.pull_request_username(pr), )
        wrap_paragraph(stream, title, wrapcol, '', '  ')
        for line in lines:
            wrap_paragraph(stream, line, wrapcol, '', '  ')
        stream.write(u'\n')
    stream.write(u'\n')


def print_source_changes(stream, wrapcol, repo, previous, current):
    def categorise(heading, item):
        heading = heading.lower()
        if (newdrivers_pat.match(heading) is not None) and (softlist_pat.match(heading) is None):
            clone = heading.find('clone') >= 0
            if heading.find('promot') >= 0:
                working = True
                promoted = True
            elif notworking_pat.search(heading) is not None:
                working = False
                promoted = False
            else:
                working = True
                promoted = False
            if clone:
                (new_promoted_clones if promoted else new_working_clones if working else new_broken_clones).append(item)
            else:
                (new_promoted_parents if promoted else new_working_parents if working else new_broken_parents).append(item)

    scraper = LogScraper(stream, wrapcol, categorise)
    print_section_heading(stream, 'Source changes')
    for commit in repo.iter_commits('%s..%s' % (previous.hexsha, current.hexsha), reverse=True):
        scraper.process_commit(commit)
    stream.write(u'\n')


def print_new_machines(stream, wrapcol, title, machines):
    if machines:
        print_section_heading(stream, title)
        for machine in machines:
            print_wrapped(stream, wrapcol, bullet_pat.sub('\\2', machine), -1)
        stream.write(u'\n\n')


def print_preliminary_whatsnew(stream, wrapcol, title, repository, api, release, candidate, verbose):
    placeholders = (
            u'%s' % (title, ),
            u'MAME Testers bugs fixed',
            u'New working machines',                    u'New working clones' ,
            u'Machines promoted to working',            u'Clones promoted to working',
            u'New machines marked as NOT_WORKING',      u'New clones marked as NOT_WORKING',
            u'New working software list additions',
            u'Software list items promoted to working',
            u'New NOT_WORKING software list additions',
            u'Translations added or modified')
    for heading in placeholders:
        print_section_heading(stream, heading)
        stream.write(u'\n\n')

    print_fresh_pull_requests(stream, wrapcol, repository, api, release, candidate)
    print_source_changes(stream, wrapcol, repository, release, candidate)
    print_new_machines(stream, wrapcol, u'New working machines', new_working_parents);
    print_new_machines(stream, wrapcol, u'New working clones', new_working_clones);
    print_new_machines(stream, wrapcol, u'Machines promoted to working', new_promoted_parents);
    print_new_machines(stream, wrapcol, u'Clones promoted to working', new_promoted_clones);
    print_new_machines(stream, wrapcol, u'New machines marked as NOT_WORKING', new_broken_parents);
    print_new_machines(stream, wrapcol, u'New clones marked as NOT_WORKING', new_broken_clones);

    comp = SoftlistComparator(stream, verbose)
    current = candidate.tree['hash']
    previous = release.tree['hash']
    for obj in current:
        if obj.type == 'blob':
            basename, extension = os.path.splitext(obj.name)
            if extension == '.xml':
                if verbose:
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
                elif verbose:
                    sys.stderr.write('no changes since previous release\n')
    for obj in previous:
        if obj.type == 'blob':
            basename, extension = os.path.splitext(obj.name)
            if extension == '.xml':
                try:
                    current / obj.name
                except KeyError:
                    if verbose:
                        sys.stderr.write('checking software list %s\n' % (obj.name, ))
                    try:
                        comp.compare(None, obj)
                    except xml.sax.SAXException as err:
                        sys.stderr.write('error processing software list %s: %s\n' % (obj.name, err))


if __name__ == '__main__':
    opts = Options()
    stream = opts.output

    if not opts.commits:
        print_preliminary_whatsnew(stream, opts.wrap, opts.title, opts.repository, opts.api, opts.release, opts.candidate, opts.verbose)
    else:
        scraper = LogScraper(stream, opts.wrap, None)
        for spec in opts.commits:
            if spec.find('..') >= 0:
                for commit in opts.repository.iter_commits(spec, reverse=True):
                    scraper.process_commit(commit)
            else:
                scraper.process_commit(opts.repository.commit(spec))
