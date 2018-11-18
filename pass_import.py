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
import re
import io
import sys
import csv
import json
import glob
import shutil
import argparse
import importlib
import configparser
from subprocess import Popen, PIPE
from collections import OrderedDict

__version__ = '2.4a'

importers = {
    '1password': ['OnePassword', 'https://1password.com/'],
    '1password4': ['OnePassword4', 'https://1password.com/'],
    '1password4pif': ['OnePassword4PIF', 'https://1password.com/'],
    'bitwarden': ['Bitwarden', 'https://bitwarden.com/'],
    'chrome': ['Chrome', 'https://support.google.com/chrome'],
    'chromesqlite': ['ChromeSQLite', 'https://support.google.com/chrome'],
    'dashlane': ['Dashlane', 'https://www.dashlane.com/'],
    'enpass': ['Enpass', 'https://www.enpass.io/'],
    'fpm': ['FigaroPM', 'http://fpm.sourceforge.net/'],
    'gorilla': ['Gorilla', 'https://github.com/zdia/gorilla/wiki'],
    'kedpm': ['FigaroPM', 'http://kedpm.sourceforge.net/'],
    'keepass': ['Keepass', 'https://www.keepass.info'],
    'keepasscsv': ['KeepassCSV', 'https://www.keepass.info'],
    'keepassx': ['KeepassX', 'https://www.keepassx.org/'],
    'keepassx2': ['KeepassX2', 'https://www.keepassx.org/'],
    'keepassxc': ['KeepassXC', 'https://keepassxc.org/'],
    'lastpass': ['Lastpass', 'https://www.lastpass.com/'],
    'networkmanager': ['NetworkManager', 'https://wiki.gnome.org/Projects/NetworkManager'],
    'passwordexporter': ['PasswordExporter', 'https://github.com/kspearrin/ff-password-exporter'],
    'pwsafe': ['Pwsafe', 'https://pwsafe.org/'],
    'revelation': ['Revelation', 'https://revelation.olasagasti.info/'],
    'roboform': ['Roboform', 'https://www.roboform.com/'],
    'upm': ['UPM', 'http://upm.sourceforge.net/'],
}


class PasswordStoreError(Exception):
    """Error in the execution of password store."""


class FormatError(Exception):
    """Password importer format (XML or CSV) not recognized."""


class Msg():
    """General class to manage output messages."""
    green = '\033[32m'
    yellow = '\033[33m'
    magenta = '\033[35m'
    Bred = '\033[1m\033[91m'
    Bgreen = '\033[1m\033[92m'
    Byellow = '\033[1m\033[93m'
    Bmagenta = '\033[1m\033[95m'
    Bold = '\033[1m'
    end = '\033[0m'

    def __init__(self, verbose=False, quiet=False):
        self.verb = verbose
        self.quiet = quiet
        if self.quiet:
            self.verb = False

    def verbose(self, title='', msg=''):
        if self.verb:
            print("%s  .  %s%s%s: %s%s" % (self.Bmagenta, self.end,
                                           self.magenta, title, self.end, msg))

    def message(self, msg=''):
        if not self.quiet:
            print("%s  .  %s%s" % (self.Bold, self.end, msg))

    def echo(self, msg=''):
        if not self.quiet:
            print("       %s" % msg)

    def success(self, msg=''):
        if not self.quiet:
            print("%s (*) %s%s%s%s" % (self.Bgreen, self.end,
                                       self.green, msg, self.end))

    def warning(self, msg=''):
        if not self.quiet:
            print("%s  w  %s%s%s%s" % (self.Byellow, self.end,
                                       self.yellow, msg, self.end))

    def error(self, msg=''):
        print("%s [x] %s%sError: %s%s" % (self.Bred, self.end,
                                          self.Bold, self.end, msg))

    def die(self, msg=''):
        self.error(msg)
        exit(1)


try:
    from defusedxml import ElementTree
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    msg = Msg()
    msg.die("""defusedxml is not present, you can install it with
     'sudo apt-get install python3-defusedxml', or
     'pip3 install defusedxml'""")


class PasswordStore():
    """Simple Password Store for python, only able to insert password.
    Supports all the environment variables.
    """
    def __init__(self):
        self.passbinary = shutil.which('pass')
        self.env = dict(**os.environ)
        self._setenv('PASSWORD_STORE_DIR')
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

        if 'PASSWORD_STORE_DIR' not in self.env:
            raise PasswordStoreError("pass prefix unknown")
        self.prefix = self.env['PASSWORD_STORE_DIR']

    def _setenv(self, var, env=None):
        """Add var in the environment variables dictionary."""
        if env is None:
            env = var
        if env in os.environ:
            self.env[var] = os.environ[env]

    def _pass(self, arg=None, data=None):
        """Call to password store."""
        command = [self.passbinary]
        if arg is not None:
            command.extend(arg)

        process = Popen(command, universal_newlines=True, env=self.env,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)  # nosec
        (stdout, stderr) = process.communicate(data)
        res = process.wait()
        if res:
            raise PasswordStoreError("%s %s" % (stderr, stdout))
        return stdout

    def insert(self, path, data, force=False):
        """Multiline insertion into the password store."""
        if not force:
            if os.path.isfile(os.path.join(self.prefix, path + '.gpg')):
                raise PasswordStoreError("An entry already exists for %s." % path)
        arg = ['insert', '--multiline']
        arg.append(path)
        return self._pass(arg, data)

    def exist(self):
        """Return True if the password store is initialized."""
        return os.path.isfile(os.path.join(self.prefix, '.gpg-id'))


class PasswordManager():
    """Common structure and methods for all password manager supported.

    Please read CONTRIBUTING.md for more details regarding data structure
    in pass-import.
    """
    keyslist = ['title', 'password', 'login', 'url', 'comments', 'group']

    def __init__(self, extra=False):
        self.data = []
        self.all = extra

    @staticmethod
    def get(entry):
        """Return the content of an entry in a password-store format."""
        string = entry.pop('password', '') + '\n'
        for key, value in entry.items():
            if key == 'path':
                continue
            string += "%s: %s\n" % (key, value)
        return string

    @staticmethod
    def _clean_protocol(entry, key):
        """Remove the protocol prefix for the value."""
        if key in entry:
            entry[key] = entry[key].replace('https://', '')
            entry[key] = entry[key].replace('http://', '')

    @staticmethod
    def _clean_cmdline(string):
        """Make the string more command line friendly."""
        caracters = {" ": "_", "&": "and", '/': '-', '\\': '-', "@": "At",
                     "'": "", "[": "", "]": ""}
        for key in caracters:
            string = string.replace(key, caracters[key])
        return string

    def _duplicate_paths(self):
        """Detect duplicate paths."""
        seen = []
        for entry in self.data:
            path = entry.get('path', '')
            if path in seen:
                ii = 0
                while path in seen:
                    if re.search('(\d+)$', path) is None:
                        path += '0'
                    else:
                        path = path.replace(str(ii), str(ii + 1))
                        ii += 1
                seen.append(path)
                entry['path'] = path
            else:
                seen.append(path)

    @staticmethod
    def _create_path(entry):
        """Create path from title and group."""
        path = entry.pop('group', '').replace('\\', '/')
        if 'title' in entry:
            path = os.path.join(path, entry.pop('title'))
        elif 'url' in entry:
            path = os.path.join(path, entry['url'].replace('http://', '').replace('https://', ''))
        elif 'login' in entry:
            path = os.path.join(path, entry['login'])
        else:
            path = os.path.join(path, 'notitle')
        return path

    def satanize(self, clean):
        """Clean parsed data in order to be imported to a store."""
        for entry in self.data:
            # Remove unused keys
            empty = [k for k, v in entry.items() if not v]
            for key in empty:
                entry.pop(key)

            self._clean_protocol(entry, 'title')
            if clean:
                entry['title'] = self._clean_cmdline(entry['title'])
            entry['path'] = self._create_path(entry)

        self._duplicate_paths()


class PasswordManagerCSV(PasswordManager):
    fieldnames = None

    def _checkline(self, file):
        line = file.readline()
        if not line.startswith(self.format):
            raise FormatError()

    def _checkformat(self, fieldnames):
        for csvkey in self.keys.values():
            if csvkey not in fieldnames:
                raise FormatError()

    def parse(self, file):
        reader = csv.DictReader(file, fieldnames=self.fieldnames,
                                delimiter=',', quotechar='"')
        self._checkformat(reader.fieldnames)

        for row in reader:
            entry = OrderedDict()
            for key in self.keyslist:
                entry[key] = row.pop(self.keys.get(key, ''), None)

            if self.all:
                for col in row:
                    entry[col] = row.get(col, None)

            self.data.append(entry)


class PasswordManagerXML(PasswordManager):

    def _checkformat(self, tree):
        if tree.tag != self.format:
            raise FormatError()

    @classmethod
    def _getroot(cls, tree):
        return tree

    @classmethod
    def _getvalue(cls, elements, xmlkey):
        value = elements.find(xmlkey)
        return '' if value is None else value.text

    def _getentry(self, element):
        entry = OrderedDict()
        for key in self.keyslist:
            xmlkey = self.keys.get(key, '')
            if xmlkey != '':
                entry[key] = self._getvalue(element, xmlkey)
        return entry

    def parse(self, file):
        tree = ElementTree.XML(file.read())
        self._checkformat(tree)
        root = self._getroot(tree)
        self._import(root)


class PasswordManagerPIF(PasswordManager):
    ignore = ['keyID', 'typeName', 'uuid', 'openContents', 'folderUuid', 'URLs']

    @staticmethod
    def _pif2json(file):
        """Convert 1pif to json see https://github.com/eblin/1passpwnedcheck."""
        data = file.read()
        cleaned = re.sub('(?m)^\*\*\*.*\*\*\*\s+', '', data)
        cleaned = cleaned.split('\n')
        cleaned = ','.join(cleaned).rstrip(',')
        cleaned = '[%s]' % cleaned
        return json.loads(cleaned)

    @staticmethod
    def _getvalue(jsonkey, item, scontent, fields):
        value = item.pop(jsonkey, None)
        value = scontent.pop(jsonkey, value)
        if value is None:
            for field in fields:
                if field.get('name', '') == jsonkey:
                    value = field.get('value', None)
                    index = fields.index(field)
                    fields.pop(index)
                    break
        return value

    def _sortgroup(self, folders):
        for folder in folders.values():
            parent = folder.get('parent', '')
            groupup = folders.get(parent, {}).get('group', '')
            folder['group'] = os.path.join(groupup, folder.get('group', ''))

        for entry in self.data:
            groupid = entry.get('group', '')
            entry['group'] = folders.get(groupid, {}).get('group', '')

    def parse(self, file):
        jsons = self._pif2json(file)
        folders = dict()
        for item in jsons:
            if item.get('typeName', '') == 'system.folder.Regular':
                key = item.get('uuid', '')
                folders[key] = {'group': item.get('title', ''),
                                'parent': item.get('folderUuid', '')}

            elif item.get('typeName', '') == 'webforms.WebForm':
                entry = OrderedDict()
                scontent = item.pop('secureContents', {})
                fields = scontent.pop('fields', [])
                for key in self.keyslist:
                    jsonkey = self.keys.get(key, '')
                    entry[key] = self._getvalue(jsonkey, item, scontent, fields)

                if self.all:
                    for field in fields:
                        entry[field.get('name', '')] = field.get('value', '')
                    item.update(scontent)
                    for key, value in item.items():
                        if key not in self.ignore:
                            entry[key] = value

                self.data.append(entry)
        self._sortgroup(folders)


class OnePassword4PIF(PasswordManagerPIF):
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'location', 'comments': 'notesPlain', 'group': 'folderUuid'}


class OnePassword4(PasswordManagerCSV):
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'notes'}


class OnePassword(PasswordManagerCSV):
    keys = {'title': 'Title', 'password': 'Password', 'login': 'Username',
            'url': 'URL', 'comments': 'Notes', 'group': 'Type'}


class Bitwarden(PasswordManagerCSV):
    keys = {'title': 'name', 'password': 'login_password', 'login': 'login_username',
            'url': 'login_uri', 'comments': 'notes', 'group': 'folder'}


class Chrome(PasswordManagerCSV):
    keys = {'title': 'name', 'password': 'password', 'login': 'username',
            'url': 'url'}


class ChromeSQLite(PasswordManagerCSV):
    keys = {'title': 'display_name', 'password': 'password_value',
            'login': 'username_value', 'url': 'origin_url'}


class Dashlane(PasswordManagerCSV):
    fieldnames = ['title', 'url', 'login', 'password', 'comments']
    keys = {'title': 'title', 'password': 'password', 'login': 'login',
            'url': 'url', 'comments': 'comments'}


class Enpass(PasswordManagerCSV):
    format = '"Title","Field","Value","Field","Value",.........,"Note"'
    keys = {'title': 'Title', 'password': 'Password', 'login': 'Username',
            'url': 'URL', 'comments': 'notes', 'group': 'group'}

    def parse(self, file):
        self._checkline(file)
        reader = csv.reader(file)
        for row in reader:
            entry = OrderedDict()
            entry['title'] = row.pop(0)
            comments = row.pop()
            for key in self.keyslist:
                csvkey = self.keys.get(key, '')
                if csvkey in row:
                    index = row.index(csvkey)
                    entry[key] = row.pop(index+1)
                    row.pop(index)
            entry['comments'] = comments

            if self.all:
                index = 0
                while index+2 <= len(row):
                    entry[row[index]] = row[index+1]
                    index += 2

            self.data.append(entry)


class FigaroPM(PasswordManagerXML):
    format = 'FPM'
    keys = {'title': 'title', 'password': 'password', 'login': 'user',
            'url': 'url', 'comments': 'notes', 'group': 'category'}

    @classmethod
    def _getroot(cls, tree):
        return tree.find('PasswordList')

    def _import(self, element):
        for xmlentry in element.findall('PasswordItem'):
            entry = self._getentry(xmlentry)
            self.data.append(entry)


class Gorilla(PasswordManagerCSV):
    keys = {'title': 'title', 'password': 'password', 'login': 'user',
            'url': 'url', 'comments': 'notes', 'group': 'group'}

    def parse(self, file):
        super(Gorilla, self).parse(file)
        for entry in self.data:
            entry['group'] = re.sub('(?<=[^\\\])\.', '/', entry['group'])
            entry['group'] = re.sub('\\\.', '.', entry['group'])


class KeepassX(PasswordManagerXML):
    group = 'group'
    entry = 'entry'
    format = 'database'
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'comment'}

    @classmethod
    def _getpath(cls, element, path=''):
        res = ''
        if element.tag != 'database':
            if element.find('title').text:
                res = os.path.join(path, element.find('title').text)
            else:
                res = os.path.join(path, 'untitled')
        return res

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

    @classmethod
    def _getroot(cls, tree):
        root = tree.find('Root')
        return root.find('Group')

    @classmethod
    def _getvalue(cls, elements, xmlkey):
        value = ''
        for element in elements:
            for child in element.findall('Key'):
                if child.text == xmlkey:
                    value = element.find('Value').text
                    break
        return value

    @classmethod
    def _getpath(cls, element, path=''):
        """Generate path name from elements title and current path."""
        title = ''
        if element.tag == 'Entry':
            title = cls._getvalue(element.findall('String'), 'Title')
        elif element.tag == 'Group':
            title = element.find('Name').text
        return os.path.join(path, title)


class KeepassCSV(PasswordManagerCSV):
    keys = {'title': 'Account', 'password': 'Password', 'login': 'Login Name',
            'url': 'Web Site', 'comments': 'Comments'}


class KeepassX2(PasswordManagerCSV):
    keys = {'title': 'Title', 'password': 'Password', 'login': 'Username',
            'url': 'URL', 'comments': 'Notes', 'group': 'Group'}


class KeepassXC(KeepassX2):
    pass


class Lastpass(PasswordManagerCSV):
    keys = {'title': 'name', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'extra', 'group': 'grouping'}


class NetworkManager(PasswordManager):
    etc = '/etc/NetworkManager/system-connections'
    keyslist = ['title', 'password', 'login', 'ssid']
    keys = {'title': 'connection.id', 'password': 'wifi-security.psk',
            'login': '802-1x.identity', 'ssid': 'wifi.ssid'}

    def parse(self, data):
        if isinstance(data, io.IOBase):
            files = [data]
        else:
            data = self.etc if data is None else data
            files = [open(path, 'r') for path in glob.glob(data + '/*')]

        for file in files:
            ini = configparser.ConfigParser()
            ini.read_file(file)
            self.keys['password'] = '802-1x.password' if '802-1x' in ini else 'wifi-security.psk'
            entry = OrderedDict()
            for key in self.keyslist:
                sect, option = self.keys.get(key, '.').split('.')
                entry[key] = ini.get(sect, option, fallback=None)

            if self.all:
                for section in ini.sections():
                    for option in ini.options(section):
                        entry[option] = ini.get(section, option, fallback=None)

            if entry.get('password', None) is not None:
                self.data.append(entry)

            file.close()


class PasswordExporter(PasswordManagerCSV):
    keys = {'title': 'hostname', 'password': 'password', 'login': 'username'}


class Pwsafe(PasswordManagerXML):
    format = 'passwordsafe'
    keyslist = ['title', 'password', 'login', 'url', 'email', 'comments', 'group']
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'email': 'email', 'comments': 'notes', 'group': 'group'}

    def _import(self, element):
        delimiter = element.attrib['delimiter']
        for xmlentry in element.findall('entry'):
            entry = self._getentry(xmlentry)
            entry['group'] = entry.get('group', '').replace('.', '/')
            entry['comments'] = entry.get('comments', '').replace(delimiter, '\n')
            if self.all:
                for historyentry in xmlentry.findall('./pwhistory/history_entries/history_entry'):
                    key = 'oldpassword' + historyentry.attrib['num']
                    time = self._getvalue(historyentry, 'changedx')
                    oldpassword = self._getvalue(historyentry, 'oldpassword')
                    entry[key] = time + ' ' + oldpassword
            self.data.append(entry)


class Revelation(PasswordManagerXML):
    format = 'revelationdata'
    keys = {'title': 'name', 'password': 'generic-password',
            'login': 'generic-username', 'url': 'generic-hostname',
            'comments': 'notes', 'group': '', 'description': 'description'}

    @classmethod
    def _getvalue(cls, elements, xmlkey):
        fieldkeys = ['generic-hostname', 'generic-username', 'generic-password']
        if xmlkey in fieldkeys:
            for field in elements.findall('field'):
                if xmlkey == field.attrib['id']:
                    return field.text
        else:
            return elements.find(xmlkey).text
        return ''

    def _import(self, element, path=''):
        for xmlentry in element.findall('entry'):
            if xmlentry.attrib.get('type', '') == 'folder':
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


class UPM(PasswordManagerCSV):
    fieldnames = ['title', 'login', 'password', 'url', 'comments']
    keys = {'title': 'title', 'password': 'password', 'login': 'login',
            'url': 'url', 'comments': 'comments'}


def main(argv):
    # Geting arguments for 'pass import'
    parser = argparse.ArgumentParser(prog='pass import', description="""
  Import data from most of the password manager. Passwords
  are imported in the existing default password store, therefore
  the password store must have been initialised before with 'pass init'""",
    usage="%(prog)s [-h] [-V] [[-p PATH] [-c] [-e] [-f] | -l] [manager] [file]",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="More information may be found in the pass-import(1) man page.")

    parser.add_argument('manager', type=str, nargs='?',
                        help="Can be: %s"
                        % ', '.join(list(importers.keys())) + '.')
    parser.add_argument('file', type=str, nargs='?',
                        help="""File is the path to the file that contains the
                        data to import, if empty read the data from stdin.""")

    parser.add_argument('-p', '--path', action='store', dest='root',
                        default='', metavar='PATH',
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
                        version='%(prog)s ' + __version__,
                        help='Show the program version and exit.')

    arg = parser.parse_args(argv)
    msg = Msg(arg.verbose, arg.quiet)

    if arg.list:
        # List supported password managers
        msg.success("The %s supported password managers are:" % len(importers))
        for name, value in importers.items():
            msg.message("%s%s%s - %s" % (msg.Bold, name, msg.end, value[1]))
    else:
        # Sanity checks
        if arg.manager is None:
            msg.die("password manager not present. See 'pass import -h'")
        if arg.manager not in importers:
            msg.die("%s is not a supported password manager" % arg.manager)
        if arg.manager == 'networkmanager' and (arg.file is None or os.path.isdir(arg.file)):
            file = arg.file
        elif arg.file is None:
            file = sys.stdin
        elif os.path.isfile(arg.file):
            encoding = 'utf-8-sig' if arg.manager == '1password4pif' else 'utf-8'
            file = open(arg.file, 'r', encoding=encoding)
        else:
            msg.die("%s is not a file" % arg.file)

        # Import and clean data
        ImporterClass = getattr(importlib.import_module(__name__),
                                importers[arg.manager][0])
        importer = ImporterClass(arg.extra)
        try:
            importer.parse(file)
            importer.satanize(arg.clean)
        except (FormatError, AttributeError, ValueError):
            msg.die("%s is not a exported %s file" % (arg.file, arg.manager))
        except PermissionError as e:
            msg.die(e)
        finally:
            if arg.manager != 'networkmanager':
                file.close()

        # Insert data into the password store
        store = PasswordStore()
        if not store.exist():
            msg.die("password store not initialized")
        for entry in importer.data:
            try:
                passpath = os.path.join(arg.root, entry['path'])
                data = importer.get(entry)
                msg.verbose("Path", passpath)
                msg.verbose("Data", data.replace('\n', '\n           '))
                store.insert(passpath, data, arg.force)
            except PasswordStoreError as e:
                msg.warning("Impossible to insert %s into the store: %s"
                            % (passpath, e))

        # Success!
        msg.success("Importing passwords from %s" % arg.manager)
        if arg.file is None:
            arg.file = 'read from stdin'
        msg.message("File: %s" % arg.file)
        if arg.root != '':
            msg.message("Root path: %s" % arg.root)
        msg.message("Number of password imported: %s" % len(importer.data))
        if arg.clean:
            msg.message("Imported data cleaned")
        if arg.extra:
            msg.message("Extra data conserved")
        msg.message("Passwords imported:")
        for entry in importer.data:
            msg.echo(os.path.join(arg.root, entry['path']))


if __name__ == "__main__":
    sys.argv.pop(0)
    main(sys.argv)
