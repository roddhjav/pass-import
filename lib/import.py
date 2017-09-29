#!/usr/bin/env python3
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017 Alexandre PUJOL <alexandre@pujol.io>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import csv
import argparse
from xml.etree import ElementTree
from subprocess import Popen, PIPE
from collections import OrderedDict


GREEN = '\033[32m'
YELLOW = '\033[33m'
MAGENTA = '\033[35m'
BRED = '\033[1m\033[91m'
BGREEN = '\033[1m\033[92m'
BYELLOW = '\033[1m\033[93m'
BMAGENTA = '\033[1m\033[95m'
BOLD = '\033[1m'
END = '\033[0m'

importers = {
    '1password': ['OnePassword', 'https://1password.com/'],
    '1password4': ['OnePassword4', 'https://1password.com/'],
    'chrome': ['Chrome', 'https://support.google.com/chrome'],
    'dashlane': ['Dashlane', 'https://www.dashlane.com/'],
    'enpass': ['Enpass', 'https://www.enpass.io/'],
    'fpm': ['FigaroPM', 'http://fpm.sourceforge.net/'],
    'gorilla': ['Gorilla', 'https://github.com/zdia/gorilla/wiki'],
    'kedpm': ['FigaroPM', 'http://kedpm.sourceforge.net/'],
    'keepass': ['Keepass', 'https://www.keepass.info'],
    'keepasscsv': ['KeepassCSV', 'https://www.keepass.info'],
    'keepassx': ['KeepassX', 'https://www.keepassx.org/'],
    'kwallet': ['Kwallet', 'https://utils.kde.org/projects/kwalletmanager/'],
    'lastpass': ['Lastpass', 'https://www.lastpass.com/'],
    'passwordexporter': ['PasswordExporter', 'https://addons.mozilla.org/en-US/firefox/addon/password-exporter/'],
    'pwsafe': ['Pwsafe', 'https://pwsafe.org/'],
    'revelation': ['Revelation', 'https://revelation.olasagasti.info/'],
    'roboform': ['Roboform', 'https://www.roboform.com/'],
}

def list_importers():
    res = ''
    for key in importers:
        res += key + ' '
    return res

def verbose(title='', msg=''):
    if arg.verbose:
        print("%s  .  %s%s%s: %s%s" % (BMAGENTA, END, MAGENTA, title, END, msg))

def message(msg=''):
    if not arg.quiet:
        print("%s  .  %s%s" % (BOLD, END, msg))

def msg(msg=''):
    if not arg.quiet:
        print("       %s" % msg)

def success(msg=''):
    if not arg.quiet:
        print("%s (*) %s%s%s%s" % (BGREEN, END, GREEN, msg, END))

def warning(msg=''):
    if not arg.quiet:
        print("%s  w  %s%s%s%s" % (BYELLOW, END, YELLOW, msg, END))

def error(msg=''):
    print("%s [x] %s%sError: %s%s" % (BRED, END, BOLD, END, msg))

def die(msg=''):
    error(msg)
    exit(1)

class PasswordStoreError(Exception):
    pass

class FormatError(Exception):
    pass

class PasswordStore():
    """ Simple Password Store for python, only able to insert password.
        Supports all the environnement variables.
    """
    def __init__(self):
        self.passbinary = "/usr/bin/pass"
        self.env = dict(**os.environ)
        self._setenv('PASSWORD_STORE_DIR', 'PREFIX')
        self._setenv('PASSWORD_STORE_KEY')
        self._setenv('PASSWORD_STORE_GIT', 'GIT_DIR')
        self._setenv('PASSWORD_STORE_GPG_OPTS')
        self._setenv('PASSWORD_STORE_X_SELECTION', 'X_SELECTION')
        self._setenv('PASSWORD_STORE_CLIP_TIME', 'CLIP_TIME')
        self._setenv('PASSWORD_STORE_UMASK')
        self._setenv('PASSWORD_STORE_GENERATED_LENGHT', 'GENERATED_LENGTH')
        self._setenv('PASSWORD_STORE_CHARACTER_SET', 'CHARACTER_SET')
        self._setenv('PASSWORD_STORE_CHARACTER_SET_NO_SYMBOLS',
                     'CHARACTER_SET_NO_SYMBOLS')
        self._setenv('PASSWORD_STORE_ENABLE_EXTENSIONS')
        self._setenv('PASSWORD_STORE_EXTENSIONS_DIR', 'EXTENSIONS')
        self._setenv('PASSWORD_STORE_SIGNING_KEY')
        self._setenv('GNUPGHOME')
        self.prefix = self.env['PASSWORD_STORE_DIR']

    def _setenv(self, var, env=None):
        """ Add var in the environnement variables directory.
            env must be an existing os environnement variables.
        """
        if env is None:
            env = var
        if env in os.environ:
            self.env[var] = os.environ[env]

    def _pass(self, arg=None, data=None):
        """ Call to password store """
        command = [self.passbinary]
        if arg is not None:
            command.extend(arg)

        process = Popen(command, universal_newlines=True, env=self.env,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = process.communicate(data)
        res = process.wait()
        if res:
            raise PasswordStoreError("%s %s" % (stderr, stdout))
        return stdout

    def insert(self, path, data, force=False):
        """ Multiline insertion into the password store. """
        arg = ['insert', '--multiline']
        if force:
            arg.append('--force')
        arg.append(path)
        return self._pass(arg, data)

class PasswordManager():

    def __init__(self, all):
        self.data = []
        self.all = all

    def get(self, password):
        """ Return the content of an entry in a password-store format. """
        entry = password.copy()
        string = ''
        if 'password' in entry:
            string = entry.pop('password', None) + '\n'
        entry.pop('path', None)
        for key, value in entry.items():
            string += "%s: %s\n" % (key, value)
        return string

    def _clean_protocol(self, entry, key):
        """ Remove the protocol prefix for the value """
        if key in entry:
            entry[key] = entry[key].replace('https://', '')
            entry[key] = entry[key].replace('http://', '')

    def satanize(self, clean):
        """ Clean parsed data in order to be imported to a store """
        for entry in self.data:
            # Remove unused keys
            empty = [k for k, v in entry.items() if not v]
            for key in empty:
                entry.pop(key, None)

            # Cleaning protocol prefix
            self._clean_protocol(entry, 'title')
            self._clean_protocol(entry, 'url')

            # Make the title more command line friendly
            if clean:
                title = entry['title'].replace(" ", "_").replace("&", "and")
                title = title.replace('/', '-').replace('\\', '-')
                title = title.replace("@", "At").replace("'", "")
                entry['title'] = title.replace("[", "").replace("]", "")

            # Create path from title and group
            path = ''
            if 'group' in entry:
                path = entry.pop('group', None).replace('\\', '/')
            if 'title' in entry:
                entry['path'] = os.path.join(path, entry.pop('title', None))
            elif 'url' in entry:
                entry['path'] = os.path.join(path, entry['url'])
            elif 'login' in entry:
                entry['path'] = os.path.join(path, entry['login'])
            else:
                entry['path'] = os.path.join(path, 'notitle')

        # Detecting duplicate paths
        seen = []
        for entry in self.data:
            path = entry['path']
            if path in seen:
                while path in seen:
                    path += '0'
                seen.append(path)
                entry['path'] = path
            else:
                seen.append(path)

class PasswordManagerCSV(PasswordManager):
    fieldnames = None

    def parse(self, file):
        reader = csv.DictReader(file, fieldnames=self.fieldnames,
                                delimiter=',', quotechar='"')
        for row in reader:
            entry = OrderedDict()
            for key, csvkey in self.keys.items():
                if csvkey is not '':
                    entry[key] = row[csvkey]
                    row.pop(csvkey, None)

            if self.all:
                for col in row:
                    entry[col] = row[col]

            self.data.append(entry)

class PasswordManagerXML(PasswordManager):

    def _checkformat(self, tree):
        if tree.tag != self.format:
            raise FormatError()

    def _getroot(self, tree):
        return tree

    def _getvalue(self, element, xmlkey):
        value = element.find(xmlkey)
        if value is None:
            return ''
        else:
            return value.text

    def _getentry(self, element):
        entry = OrderedDict()
        for key, xmlkey in self.keys.items():
            if xmlkey is not '':
                value = self._getvalue(element, xmlkey)
                if value is not None and not len(value) == 0:
                    entry[key] = value
        return entry

    def parse(self, file):
        tree = ElementTree.XML(file.read())
        self._checkformat(tree)
        root = self._getroot(tree)
        self._import(root)

class OnePassword4(PasswordManagerCSV):
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'notes'}

class OnePassword(PasswordManagerCSV):
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'urls', 'comments': 'notesPlain', 'group': 'tags'}

class Chrome(PasswordManagerCSV):
    keys = {'title': 'origin_url', 'password': 'password_value',
            'login': 'username_value'}

class Dashlane(PasswordManagerCSV):
    fieldnames = ['title', 'url', 'login', 'password', 'comments']
    keys = {'title': 'title', 'password': 'password', 'login': 'login',
            'url': 'url', 'comments': 'comments'}

class Enpass(PasswordManagerCSV):
    firstline = '"Title","Field","Value","Field","Value",.........,"Note"'
    keys = {'title': 'Title', 'password': 'Password', 'login': 'UserName',
            'url': 'URL', 'comments': 'notes', 'group': 'group'}

    def parse(self, file):
        line = file.readline()
        if not line.startswith(self.firstline):
            raise FormatError()

        reader = csv.reader(file)
        for row in reader:
            entry = OrderedDict()
            entry['title'] = row.pop(0)
            comments = row.pop()
            for key, csvkey in self.keys.items():
                if csvkey in row:
                    index = row.index(csvkey)
                    entry[key] = row[index+1]
                    row.pop(index+1)
                    row.pop(index)
            entry['comments'] = comments

            if self.all:
                index = 0
                while index < len(row):
                    entry[row[index]] = row[index+1]
                    index += 2

            self.data.append(entry)

class FigaroPM(PasswordManagerXML):
    format = 'FPM'
    keys = {'title': 'title', 'password': 'password', 'login': 'user',
            'url': 'url', 'comments': 'notes', 'group': 'category'}

    def _getroot(self, tree):
        return tree.find('PasswordList')

    def _import(self, element):
        for xmlentry in element.findall('PasswordItem'):
            entry = self._getentry(xmlentry)
            self.data.append(entry)

class Gorilla(PasswordManagerCSV):
    keys = {'title': 'title', 'password': 'password', 'login': 'user',
            'url': 'url', 'comments': 'notes', 'group': 'group'}

class KeepassX(PasswordManagerXML):
    group = 'group'
    entry = 'entry'
    format = 'database'
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'comment'}

    def _getpath(self, element, path=''):
        if element.tag == 'database':
            return ''
        else:
            return os.path.join(path, element.find('title').text)

    def _import(self, element, path=''):
        path = self._getpath(element, path)
        for group in element.findall(self.group):
            self._import(group, path)
        for xmlentry in element.findall(self.entry):
            entry = self._getentry(xmlentry)
            entry['title'] = self._getpath(xmlentry)
            entry['group'] = path
            self.data.append(entry)

class Keepass(KeepassX):
    group = 'Group'
    entry = 'Entry'
    format = 'KeePassFile'
    keys = {'title': 'Title', 'password': 'Password', 'login': 'UserName',
            'url': 'URL', 'comments': 'Notes'}

    def _getroot(self, tree):
        root = tree.find('Root')
        return root.find('Group')

    def _getvalue(self, elements, text):
        for element in elements:
            for child in element.findall('Key'):
                if child.text == text:
                    return element.find('Value').text
        return ''

    def _getpath(self, element, path=''):
        """ Generate path name from elements title and current path """
        if element.tag == 'Entry':
            title = self._getvalue(element.findall('String'), 'Title')
        elif element.tag == 'Group':
            title = element.find('Name').text
        else:
            title = ''
        return os.path.join(path, title)

class KeepassCSV(PasswordManagerCSV):
    keys = {'title': 'Account', 'password': 'Password', 'login': 'Login Name',
            'url': 'Web Site', 'comments': 'Comments'}

class Lastpass(PasswordManagerCSV):
    keys = {'title': 'name', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'extra', 'group': 'grouping'}

class PasswordExporter(PasswordManagerCSV):
    firstline = '# Generated by Password Exporter, Export format 1.1, Encrypted: undefined'
    keys = {'title': 'hostname', 'password': 'password', 'login': 'username'}

    def parse(self, file):
        line = file.readline()
        if not line.startswith(self.firstline):
            raise FormatError()
        super(PasswordExporter, self).parse(file)

class Pwsafe(PasswordManagerXML):
    format = 'passwordsafe'
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'notes', 'group': 'group'}

    def _import(self, element):
        for xmlentry in element.findall('entry'):
            entry = self._getentry(xmlentry)
            if 'group' in entry:
                entry['group'] = entry['group'].replace('.', '/')
            self.data.append(entry)

class Revelation(PasswordManagerXML):
    format = 'revelationdata'
    keys = {'title': 'name', 'password': 'generic-password',
            'login': 'generic-username', 'url': 'generic-hostname',
            'comments': 'notes', 'group': '', 'description': 'description'}

    def _getvalue(self, element, xmlkey):
        fieldkeys = ['generic-hostname', 'generic-username', 'generic-password']
        if xmlkey in fieldkeys:
            for field in element.findall('field'):
                if xmlkey == field.attrib['id']:
                    return field.text
        else:
            return element.find(xmlkey).text

    def _import(self, element, path=''):
        for xmlentry in element.findall('entry'):
            if xmlentry.attrib['type'] == 'folder':
                if path != xmlentry.find('name').text:
                    path = ''
                path = os.path.join(path, xmlentry.find('name').text)
                self._import(xmlentry, path)
            else:
                entry = self._getentry(xmlentry)
                entry['group'] = path
                self.data.append(entry)

class Roboform(PasswordManagerCSV):
    keys = {'title': 'Name', 'password': 'Pwd', 'login': 'Login', 'url': 'Url',
            'comments': 'Note', 'group': 'Folder'}


if __name__ == "__main__":
    # Geting arguments for 'pass import'
    parser = argparse.ArgumentParser(prog='pass import', description="""
  Import data from most of the password manager. Passwords
  are imported in the existing default password store, therefore
  the password store must has been initialized before with 'pass init'""",
    usage="%(prog)s [-h] [-V] [[-p PATH] [-c] [-e] [-f] | -l] [manager] [file]",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="More information may be found in the pass-import(1) man page.")

    parser.add_argument('manager', type=str, nargs='?',
                        help="Can be: %s" % list_importers())
    parser.add_argument('file', type=str, nargs='?',
                        help="""File is the path to the file that contains the
                        data to import, if empty read the data from stdin.""")

    parser.add_argument('-p', '--path', action='store', dest='root', default='',
                        help='Import the passwords to a specific subfolder.')
    parser.add_argument('-c', '--clean', action='store_true',
                        help='Clean data before import.')
    parser.add_argument('-e', '--extra', action='store_true',
                        help='Also import all the extra data present.')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List the supported password managers.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Overwrite existing path.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Be quiet.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose.')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 2.0',
                        help='Show the program version and exit.')

    arg = parser.parse_args()
    if arg.quiet:
        arg.verbose = False

    if arg.list:
        # List supported password managers
        success("The %s supported password managers are:" % len(importers))
        for name, value in importers.items():
            message("%s%s%s - %s" % (BOLD, name, END, value[1]))
    else:
        # Sanity checks
        if arg.manager is None:
            die("password manager not present. See 'pass import -h'")
        if arg.manager not in importers:
            die("%s is not a supported password manager" % arg.manager)
        if arg.file is None:
            file = sys.stdin
        elif os.path.isfile(arg.file):
            file = open(arg.file, 'r', encoding='utf-8')
        else:
            die("%s is not a file" % arg.file)

        # Import and clean data
        ImporterClass = getattr(__import__('import'), importers[arg.manager][0])
        importer = ImporterClass(arg.extra)
        try:
            importer.parse(file)
            importer.satanize(arg.clean)
        except FormatError:
            die("%s is not a exported %s file" % (arg.file, arg.manager))
        finally:
            file.close()

        # Insert data into the password store
        store = PasswordStore()
        if not store.exist():
            die("password store not initialized")
        for entry in importer.data:
            try:
                passpath = os.path.join(arg.root, entry['path'])
                data = importer.get(entry)
                verbose("Path", passpath)
                verbose("Data", data.replace('\n', '\n           '))
                store.insert(passpath, data, arg.force)
            except PasswordStoreError as e:
                warning("Imposible to insert %s into the store: %s"
                        % (passpath, e))

        # Success!
        success("Importing passwords from %s" % arg.manager)
        if arg.file is None:
            arg.file = 'read from stdin'
        message("File: %s" % arg.file)
        if arg.root is not '':
            message("Root path: %s" % arg.root)
        message("Number of password imported: %s" % len(importer.data))
        if arg.clean:
            message("Imported data cleaned")
        if arg.extra:
            message("Extra data conserved")
        message("Passwords imported:")
        for entry in importer.data:
            msg(entry['path'])
