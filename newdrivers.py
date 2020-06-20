#!/usr/bin/python
##
## license:BSD-3-Clause
## copyright-holders:Vas Crabb

import codecs
import sys
import xml.sax
import xml.sax.handler


class ErrorHandler(object):
    def __init__(self, **kwargs):
        super(ErrorHandler, self).__init__(**kwargs)
        self.errors = 0
        self.warnings = 0

    def error(self, exception):
        self.errors += 1
        sys.stderr.write('error: %s\n' % (exception))

    def fatalError(self, exception):
        raise exception

    def warning(self, exception):
        self.warnings += 1
        sys.stderr.write('warning: %s\n' % (exception))


class Categoriser(object):
    def __init__(self, error_handler, **kwargs):
        super(Categoriser, self).__init__(**kwargs)

        # handling the XML
        self.error_handler = error_handler
        self.locator = None

        # parse state
        self.in_document = False
        self.in_mame = False
        self.in_machine = False
        self.in_description = False
        self.ignored_depth = 0

        # attributes of current driver
        self.driver = None
        self.is_clone = None
        self.description = None
        self.is_working = None

        # output
        self.build = None

    def startElement(self, name, attrs):
        if not self.in_document:
            self.error_handler.fatalError(xml.sax.SAXParseException(
                    'Got start of element outside document',
                    None,
                    self.locator))
        elif self.ignored_depth > 0:
            self.ignored_depth += 1
        elif not self.in_mame:
            if name != 'mame':
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Found unexpected element %s' % (name),
                        None,
                        self.locator))
            elif 'build' not in attrs:
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Expected attribute build not found',
                        None,
                        self.locator))
            else:
                self.in_mame = True
                self.build = attrs['build']
        elif not self.in_machine:
            if name != 'machine':
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Found unexpected element %s' % (name),
                        None,
                        self.locator))
            elif 'name' not in attrs:
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'Expected attribute name not found',
                        None,
                        self.locator))
            elif (('isdevice' in attrs) and (attrs['isdevice'] == 'yes')) or (('runnable' in attrs) and (attrs['runnable'] == 'no')):
                self.ignored_depth = 1
            else:
                self.in_machine = True
                self.driver = attrs['name']
                self.is_clone = 'cloneof' in attrs
        elif not self.in_description:
            if name == 'description':
                self.in_description = True
                self.description = ''
            else:
                if name == 'driver':
                    if 'emulation' not in attrs:
                        self.error_handler.fatalError(xml.sax.SAXParseException(
                                'Expected attribute status not found',
                                None,
                                self.locator))
                    else:
                        self.is_working = attrs['emulation'] != 'preliminary'
                self.ignored_depth = 1
        else:
            self.ignored_depth = 1

    def endElement(self, name):
        if self.ignored_depth > 0:
            self.ignored_depth -= 1
        elif self.in_description:
            if name != 'description':
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'End of element %s does not match start of element description' % (name),
                        None,
                        self.locator))
            else:
                self.in_description = False
        elif self.in_machine:
            if name != 'machine':
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'End of element %s does not match start of element machine' % (name),
                        None,
                        self.locator))
            else:
                if self.description is None:
                    self.error_handler.error(xml.sax.SAXParseException(
                            'Expected element description not found',
                            None,
                            self.locator))
                elif self.is_working is None:
                    self.error_handler.error(xml.sax.SAXParseException(
                            'Expected element driver not found',
                            None,
                            self.locator))
                else:
                    self.handleMachine(self.driver, self.description, self.is_clone, self.is_working)
                self.in_machine = False
                self.driver = None
                self.is_clone = None
                self.description = None
                self.is_working = None
        elif self.in_mame:
            if name != 'mame':
                self.error_handler.fatalError(xml.sax.SAXParseException(
                        'End of element %s does not match start of element mame' % (name),
                        None,
                        self.locator))
            else:
                self.in_mame = False
        else:
            self.error_handler.fatalError(xml.sax.SAXParseException(
                    'Found unexpected end of element %s' % (name),
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
        if self.in_mame:
            self.error_handler.fatalError(xml.sax.SAXParseException(
                    'Got end of document inside mame element',
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


if sys.stdout.encoding is None:
    output = codecs.getwriter('utf-8')(sys.stdout)
else:
    output = sys.stdout


def printResult(title, descriptions):
    if descriptions:
        output.write(u'%s\n' % (title, ))
        output.write(u'%s\n' % (u'-' * len(title), ))
        for description in sorted(descriptions):
             output.write(u'%s\n' % (description, ))
        output.write(u'\n')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:')
        print('  newdrivers <old.xml> <new.xml>')
        print('')
        sys.exit(0)

    oldlist = sys.argv[1]
    newlist = sys.argv[2]

    error_handler = ErrorHandler()
    content_handler = Categoriser(error_handler)
    parser = xml.sax.make_parser()
    parser.setErrorHandler(error_handler)
    parser.setContentHandler(content_handler)

    old_working = dict()
    old_nonworking = dict()
    old_descriptions = dict()
    def handleOldMachine(driver, description, is_clone, is_working):
        if is_working: old_working[driver] = description
        else: old_nonworking[driver] = description
        old_descriptions[description] = driver
    content_handler.handleMachine = handleOldMachine
    parser.parse(oldlist)
    oldbuild = content_handler.build

    new_working = dict()
    new_nonworking = dict()
    new_working_parents = set()
    new_working_clones = set()
    promoted_parents = set()
    promoted_clones = set()
    new_nonworking_parents = set()
    new_nonworking_clones = set()
    renames = dict()
    def handleNewMachine(driver, description, is_clone, is_working):
        if is_working: new_working[driver] = description
        else: new_nonworking[driver] = description
        if (driver in old_working) or (driver in old_nonworking): old_name = driver
        elif description in old_descriptions: old_name = old_descriptions[description]
        else: old_name = None
        if (old_name is None) or (old_name in renames):
            if is_working:
                if is_clone: new_working_clones.add(description)
                else: new_working_parents.add(description)
            else:
                if is_clone: new_nonworking_clones.add(description)
                else: new_nonworking_parents.add(description)
        else:
            if old_name != driver:
                renames[old_name] = (description, driver)
                if old_name in new_working: new_working_clones.add(new_working[old_name])
                elif old_name in new_nonworking: new_nonworking_clones.add(new_nonworking[old_name])
            if is_working and (old_name not in old_working):
                if is_clone: promoted_clones.add(description)
                else: promoted_parents.add(description)
    content_handler.handleMachine = handleNewMachine
    parser.parse(newlist)
    newbuild = content_handler.build

    if (error_handler.errors > 0) or (error_handler.warnings > 0):
        sys.exit(1)

    removed = list()
    for driver in old_working:
        if (driver not in new_working) and (driver not in new_nonworking) and (driver not in renames):
            removed.append(old_working[driver])
    for driver in old_nonworking:
        if (driver not in new_working) and (driver not in new_nonworking) and (driver not in renames):
            removed.append(old_nonworking[driver])
    removed.sort()

    output.write(u'Comparing %s to %s\n\n' % (oldbuild, newbuild))

    if renames:
        output.write(u'Renames\n')
        for old_name, info in renames.items():
            output.write(u'%s -> %s %s\n' % (old_name, info[1], info[0]))
        output.write(u'\n')

    if removed:
        output.write(u'Removed\n')
        for description in removed:
            output.write(u'%s\n' % (description, ))
        output.write(u'\n')

    printResult(u'New working machines', new_working_parents)
    printResult(u'New working clones', new_working_clones)
    printResult(u'Machines promoted to working', promoted_parents)
    printResult(u'Clones promoted to working', promoted_clones)
    printResult(u'New machines marked as NOT_WORKING', new_nonworking_parents)
    printResult(u'New clones marked as NOT_WORKING', new_nonworking_clones)
