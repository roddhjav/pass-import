#!/usr/bin/env python3
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017-2019 Alexandre PUJOL <alexandre@pujol.io>.
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
from collections import OrderedDict, defaultdict

__version__ = '2.4'

importers = {
    '1password': ['OnePassword', 'https://1password.com/'],
    '1password4': ['OnePassword4', 'https://1password.com/'],
    '1password4pif': ['OnePassword4PIF', 'https://1password.com/'],
    'apple-keychain': ['AppleKeychain', 'https://support.apple.com/guide/keychain-access'],
    'bitwarden': ['Bitwarden', 'https://bitwarden.com/'],
    'buttercup': ['Buttercup', 'https://buttercup.pw/'],
    'chrome': ['Chrome', 'https://support.google.com/chrome'],
    'chromesqlite': ['ChromeSQLite', 'https://support.google.com/chrome'],
    'dashlane': ['Dashlane', 'https://www.dashlane.com/'],
    'enpass': ['Enpass', 'https://www.enpass.io/'],
    'enpass6': ['Enpass6', 'https://www.enpass.io/'],
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
    """Password importer format (CSV, XML, JSON or TXT) not recognized."""


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
        self._passbinary = shutil.which('pass')
        self._gpgbinary = shutil.which('gpg2') or shutil.which('gpg')
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

    def _call(self, command, data=None):
        """Call to a command."""
        process = Popen(command, universal_newlines=True, env=self.env,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)  # nosec
        (stdout, stderr) = process.communicate(data)
        res = process.wait()
        return res, stdout, stderr

    def _pass(self, arg=None, data=None):
        """Call to password store."""
        command = [self._passbinary]
        if arg is not None:
            command.extend(arg)

        res, stdout, stderr = self._call(command, data)
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

    def is_valid_recipients(self):
        """Ensure the GPG keyring is usable."""
        with open(os.path.join(self.prefix, '.gpg-id'), 'r') as file:
            gpgids = file.read().split('\n')
            gpgids.pop()

        # All the public gpgids must be present in the keyring.
        cmd = [self._gpgbinary, '--list-keys']
        for gpgid in gpgids:
            res, _, _ = self._call(cmd + [gpgid])
            if res:
                return False

        # At least one private key must be present in the keyring.
        cmd = [self._gpgbinary, '--list-secret-keys']
        for gpgid in gpgids:
            res, _, _ = self._call(cmd + [gpgid])
            if res == 0:
                return True
        return False


class PasswordManager():
    """Common structure and methods for all password manager supported.

    Please read CONTRIBUTING.md for more details regarding data structure
    in pass-import.
    """
    keyslist = ['title', 'password', 'login', 'url', 'comments', 'group']

    def __init__(self, extra=False, separator='-'):
        self.data = []
        self.all = extra
        self.separator = str(separator)
        self.cleans = {" ": self.separator, "&": "and", "@": "At", "'": "",
                       "[": "", "]": ""}
        self.protocols = ['http://', 'https://']
        self.invalids = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\0']

    def get(self, entry):
        """Return the content of an entry in a password-store format."""
        ignore = ['title', 'group', 'path']
        string = entry.pop('password', '') + '\n'
        for key in self.keyslist:
            if key in ignore:
                continue
            if key in entry:
                string += "%s: %s\n" % (key, entry.pop(key))

        if self.all:
            for key, value in entry.items():
                if key in ignore:
                    continue
                string += "%s: %s\n" % (key, value)
        return string

    @staticmethod
    def _replaces(caracters, string):
        """Global replace method."""
        for key in caracters:
            string = string.replace(key, caracters[key])
        return string

    def _clean_protocol(self, string):
        """Remove the protocol prefix in a string."""
        caracters = dict(zip(self.protocols, ['']*len(self.protocols)))
        return self._replaces(caracters, string)

    def _clean_group(self, string):
        """Remove invalids caracters in a group. Convert separator to os.sep."""
        caracters = dict(zip(self.invalids, [self.separator]*len(self.invalids)))
        caracters['/'] = os.sep
        caracters['\\'] = os.sep
        return self._replaces(caracters, string)

    def _convert(self, string):
        """Convert invalid caracters by the separator in a string."""
        caracters = dict(zip(self.invalids, [self.separator]*len(self.invalids)))
        return self._replaces(caracters, string)

    def _clean_cmdline(self, string):
        """Make the string more command line friendly."""
        return self._replaces(self.cleans, string)

    def _duplicate_paths(self, clean, convert):
        """Create subfolders for duplicated paths."""
        duplicated = defaultdict(list)
        for idx, entry in enumerate(self.data):
            path = entry.get('path', '')
            duplicated[path].append(idx)

        for path in duplicated:
            if len(duplicated[path]) > 1:
                for idx in duplicated[path]:
                    entry = self.data[idx]
                    entry['path'] = self._create_path(entry, path, clean, convert)

    def _duplicate_numerise(self):
        """Add number to the remaining duplicated path."""
        seen = []
        for entry in self.data:
            path = entry.get('path', '')
            if path in seen:
                ii = 1
                while path in seen:
                    if re.search('%s(\d+)$' % self.separator, path) is None:
                        path += self.separator + str(ii)
                    else:
                        path = path.replace(self.separator + str(ii),
                                            self.separator + str(ii + 1))
                        ii += 1
                seen.append(path)
                entry['path'] = path
            else:
                seen.append(path)

    def _create_path(self, entry, path, clean, convert):
        """Create path from title and group."""
        title = ''
        for key in ['title', 'login', 'url']:
            if key in entry:
                title = self._clean_protocol(entry[key])
                if clean:
                    title = self._clean_cmdline(title)
                if convert:
                    title = self._convert(title)
                path = os.path.join(path, title)
                break

        if title == '':
            path = os.path.join(path, 'notitle')
        entry.pop('title', '')
        return path

    def _invkeys(self):
        """Return the invert of self.keys."""
        return {v: k for k, v in self.keys.items()}

    def clean(self, clean, convert):
        """Clean parsed data in order to be imported to a store."""
        for entry in self.data:
            # Remove unused keys
            empty = [k for k, v in entry.items() if not v]
            for key in empty:
                entry.pop(key)

            path = self._clean_group(self._clean_protocol(entry.pop('group', '')))
            entry['path'] = self._create_path(entry, path, clean, convert)

        self._duplicate_paths(clean, convert)
        self._duplicate_numerise()


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

        keys = self._invkeys()
        for row in reader:
            entry = dict()
            for col in row:
                entry[keys.get(col, col)] = row.get(col, None)

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


class PasswordManagerJSON(PasswordManager):

    def _sortgroup(self, folders):
        for folder in folders.values():
            parent = folder.get('parent', '')
            groupup = folders.get(parent, {}).get('group', '')
            folder['group'] = os.path.join(groupup, folder.get('group', ''))

        for entry in self.data:
            groupid = entry.get('group', '')
            entry['group'] = folders.get(groupid, {}).get('group', '')


class PasswordManagerPIF(PasswordManagerJSON):
    ignore = ['keyID', 'typeName', 'uuid', 'openContents', 'URLs']

    @staticmethod
    def _pif2json(file):
        """Convert 1pif to json see https://github.com/eblin/1passpwnedcheck."""
        data = file.read()
        cleaned = re.sub('(?m)^\*\*\*.*\*\*\*\s+', '', data)
        cleaned = cleaned.split('\n')
        cleaned = ','.join(cleaned).rstrip(',')
        cleaned = '[%s]' % cleaned
        return json.loads(cleaned)

    def parse(self, file):
        jsons = self._pif2json(file)
        keys = self._invkeys()
        folders = dict()
        for item in jsons:
            if item.get('typeName', '') == 'system.folder.Regular':
                key = item.get('uuid', '')
                folders[key] = {'group': item.get('title', ''),
                                'parent': item.get('folderUuid', '')}

            elif item.get('typeName', '') == 'webforms.WebForm':
                entry = dict()
                scontent = item.pop('secureContents', {})
                fields = scontent.pop('fields', [])
                for field in fields:
                    jsonkey = field.get('name', '')
                    entry[keys.get(jsonkey, jsonkey)] = field.get('value', '')

                item.update(scontent)
                for key, value in item.items():
                    if key not in self.ignore:
                        entry[keys.get(key, key)] = value
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


class AppleKeychain(PasswordManager):
    @staticmethod
    def _decode_hex(strhex):
        """Decode a string with an hexadecimal value to UTF-8"""
        hexmod = strhex
        if hexmod.startswith('0x'):
            hexmod = hexmod[2:]
        if hexmod.endswith('0a') or hexmod.endswith('0A'):
            hexmod = hexmod[:-2]
        try:
            return bytes.fromhex(hexmod).decode('utf-8')
        except UnicodeError:
            return None

    @staticmethod
    def _match_pair_to_dict(match, hexkey, txtkey):
        hex_match = match.group(hexkey)
        txt_match = match.group(txtkey)
        data = dict()
        if hex_match:
            data['hex'] = hex_match
        if txt_match:
            data['txt'] = txt_match
        return data

    @staticmethod
    def _parse_attribute(line, entry):
        regex = '^\s*(?:"(?P<txtkey>\w*)"|(?P<hexkey>0x[a-zA-Z0-9]*))'\
                '\s*(?:<(?P<type>\w*)>)?'\
                '\s*='\
                '\s*(?P<hexdata>0x[a-zA-Z0-9]*)?'\
                '\s*(?:"(?P<txtdata>.*)")?'
        match = re.search(regex, line)
        if not match:
            raise FormatError()

        hexkey = match.group('hexkey')
        txtkey = match.group('txtkey')
        key = hexkey if hexkey else txtkey
        if not key:
            raise FormatError()

        data = AppleKeychain._match_pair_to_dict(match, 'hexdata', 'txtdata')
        if data:
            entry['attributes'][key] = data

    @staticmethod
    def _parse_data_filed(line, entry):
        match = re.search('^\s*(?P<hex>0x[a-zA-Z0-9]*)?\s*(?:"(?P<txt>.*)")?', line)
        if not match:
            raise FormatError()

        entry['data'] = AppleKeychain._match_pair_to_dict(match, 'hex', 'txt')

    @staticmethod
    def _parse_field(line, entry):
        match = re.search('^(?P<key>\w+):\s*(?P<hex>0x[a-zA-Z0-9]*)?\s*(?P<txt>.*)', line)
        key = match.group('key')
        if not match or not key:
            raise FormatError()

        data = AppleKeychain._match_pair_to_dict(match, 'hex', 'txt')
        if 'txt' in data:
            txt = data['txt']
            if txt.startswith('"') and txt.endswith('"'):
                data['txt'] = txt[1:-1]
        entry[key] = data

    @staticmethod
    def _parse_note_plist(plist):
        """Notes are stored in ASCII plist: extract the actual content."""
        try:
            tree = ElementTree.XML(plist)
        except ElementTree.ParseError:
            return None

        found = tree.find('.//string')
        if found is None:
            return None
        return found.text

    @staticmethod
    def _value_from_hextxt(data):
        """Return a value from data with a hex-txt pair"""
        value = ''
        if 'hex' in data:
            decoded = AppleKeychain._decode_hex(data['hex'])
            if decoded:
                value = decoded
            else:
                if 'txt' in data:
                    value = data['txt']
                else:
                    value = data['hex']
        elif 'txt' in data:
            value = data['txt']
        return value

    @staticmethod
    def _compose_url(attributes):
        """Compose the URL from the attributes of an entry fixing non-standard protocol names"""
        substitutions = {'htps': 'https', 'ldps': 'ldaps', 'ntps': 'nntps', 'sox': 'socks',
                'teln': 'telnet', 'tels': 'telnets', 'imps': 'imaps', 'pops': 'pop3s'}
        url = attributes.get('ptcl', {}).get('txt', '')
        if url:
            url = url.strip()
            url = substitutions.get(url, url)
            url += '://'
        url += attributes.get('srvr', {}).get('txt', '')
        url += attributes.get('path', {}).get('txt', '')
        return url

    @staticmethod
    def _humanize_key(key):
        human_keys = {
            '0x00000007': 'title',
            'acct': 'login',
            'atyp': 'authentication_type',
            'cdat': 'creation_date',
            'crtr': 'creator',
            'desc': 'description',
            'icmt': 'alt_comment',
            'mdat': 'modification_date',
            'path': 'password_path',
            'port': 'port',
            'ptcl': 'protocol',
            'sdmn': 'security_domain',
            'srvr': 'server',
            'svce': 'service',
            'type': 'type'
        }
        return human_keys.get(key, key)

    @staticmethod
    def _convert_entry(entry):
        """Returns an entry in pass format from an entry in keychain parsed format"""
        passentry = dict()
        title = entry['attributes'].get('0x00000007', None)
        for attr in entry['attributes']:
            # Keychain duplicates 0x07 and svce by default
            if attr == 'svce' and title == entry['attributes']['svce']:
                continue
            if attr in ['ptcl', 'srvr', 'path']:
                continue

            value = AppleKeychain._value_from_hextxt(entry['attributes'][attr])
            if value:
                key = AppleKeychain._humanize_key(attr)
                passentry[key] = value

        passentry['url'] = AppleKeychain._compose_url(entry['attributes'])

        isNote = False
        typevalue = AppleKeychain._value_from_hextxt(entry['attributes'].get('type', {}))
        if typevalue == 'note':
            passentry['group'] = 'Notes'
            isNote = True

        value = AppleKeychain._value_from_hextxt(entry.get('data', {}))
        if not re.match('^0x0[aA]$', value):
            if isNote:
                note = AppleKeychain._parse_note_plist(value)
                if note:
                    value = note
                passentry['comments'] = value
            else:
                passentry['password'] = value

        return passentry

    def parse(self, file):
        entry = dict()
        dataField = False

        for line in file:
            if dataField:
                self._parse_data_filed(line, entry)
                dataField = False
            else:
                if re.match('^\s+', line):
                    self._parse_attribute(line, entry)
                else:
                    if line.startswith('attributes:'):
                        entry['attributes'] = dict()
                    elif line.startswith('data:'):
                        dataField = True
                    else:
                        self._parse_field(line, entry)

            if 'password' in entry or 'data' in entry:
                if entry['class'].get('txt', None) not in ['genp', 'inet']:
                    return
                entry = self._convert_entry(entry)
                self.data.append(entry)
                entry = dict()


class Bitwarden(PasswordManagerCSV):
    keys = {'title': 'name', 'password': 'login_password', 'login': 'login_username',
            'url': 'login_uri', 'comments': 'notes', 'group': 'folder'}


class Buttercup(PasswordManagerCSV):
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'URL', 'comments': 'Notes', 'group': '!group_name'}
    ignore = ['!group_id', 'id']

    def parse(self, file):
        super(Buttercup, self).parse(file)
        for entry in self.data:
            for key in self.ignore:
                entry.pop(key, None)


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
        keys = self._invkeys()
        for row in reader:
            entry = dict()
            entry['title'] = row.pop(0)
            entry['comments'] = row.pop()
            index = 0
            while index+2 <= len(row):
                key = keys.get(row[index], row[index])
                entry[key] = row[index+1]
                index += 2

            self.data.append(entry)


class Enpass6(PasswordManagerJSON):
    keyslist = ['title', 'password', 'login', 'url', 'comments', 'group', 'email']
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'website', 'comments': 'note', 'group': 'group', 'email': 'e-mail'}
    ignore = ['fields', 'folders', 'icon']

    def parse(self, file):
        jsons = json.loads(file.read())
        keys = self._invkeys()
        folders = dict()
        for item in jsons.get('folders', {}):
            key = item.get('uuid', '')
            folders[key] = {'group': item.get('title', ''),
                            'parent': item.get('parent_uuid', '')}

        for item in jsons.get('items', {}):
            entry = dict()
            entry['group'] = item.get('folders', [''])[0]
            for key, value in item.items():
                if key not in self.ignore:
                    entry[keys.get(key, key)] = value

            fields = item.get('fields', {})
            for field in fields:
                jsonkey = field.get('label', '').lower()
                entry[keys.get(jsonkey, jsonkey)] = field.get('value', '')

            self.data.append(entry)
        self._sortgroup(folders)


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
            entry['group'] = re.sub('(?<=[^\\\])\.', os.sep, entry['group'])
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
                res = os.path.join(path, 'notitle')
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
    default = '/etc/NetworkManager/system-connections'
    keyslist = ['title', 'password', 'login', 'ssid']
    keys = {'title': 'connection.id', 'password': 'wifi-security.psk',
            'login': '802-1x.identity', 'ssid': 'wifi.ssid'}

    def parse(self, data):
        if isinstance(data, io.IOBase):
            files = [data]
        else:
            data = self.default if data is None else data
            files = [open(path, 'r') for path in glob.glob(data + '/*')]

        keys = self._invkeys()
        keys['802-1x.password'] = 'password'
        for file in files:
            ini = configparser.ConfigParser()
            ini.read_file(file)
            entry = dict()

            for section in ini.sections():
                for option in ini.options(section):
                    inikey = "%s.%s" % (section, option)
                    entry[keys.get(inikey, inikey)] = ini.get(section, option, fallback='')

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
            entry['group'] = entry.get('group', '').replace('.', os.sep)
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
                _path = os.path.join(path, xmlentry.find('name').text)
                self._import(xmlentry, _path)
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


def argumentsparse(argv):
    """Geting arguments for 'pass import'."""
    parser = argparse.ArgumentParser(prog='pass import', description="""
  Import data from most of the password manager. Passwords
  are imported in the existing default password store, therefore
  the password store must have been initialised before with 'pass init'""",
    usage="%(prog)s [-h] [-V] [[-p PATH] [-c] [-C] [-s] [-e] [-f] | -l] <manager> [file]",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="More information may be found in the pass-import(1) man page.")

    parser.add_argument('manager', type=str, nargs='?',
                        help="Can be: %s"
                        % ', '.join(importers) + '.')
    parser.add_argument('file', type=str, nargs='?',
                        help="""File is the path to the file that contains the
                        data to import, if empty read the data from stdin.""")

    parser.add_argument('-p', '--path', action='store', dest='root',
                        default='', metavar='PATH',
                        help='Import the passwords to a specific subfolder.')
    parser.add_argument('-e', '--extra', action='store_true',
                        help='Also import all the extra data present.')
    parser.add_argument('-c', '--clean', action='store_true',
                        help='Make the paths more command line friendly.')
    parser.add_argument('-C', '--convert', action='store_true',
                        help='Convert the invalid caracters present in the paths.')
    parser.add_argument('-s', '--separator', action='store', dest='separator',
                        metavar='CAR',
                        help="""Provide a caracter of replacement for the path
                         separator. Default: '-' """)
    parser.add_argument('-l', '--list', action='store_true',
                        help='List the supported password managers.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Overwrite existing path.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Be quiet.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose.')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __version__,
                        help='Show the program version and exit.')

    return parser.parse_args(argv)


def listimporters(msg):
    """List supported password managers."""
    msg.success("The %s supported password managers are:" % len(importers))
    for name, value in importers.items():
        msg.message("%s%s%s - %s" % (msg.Bold, name, msg.end, value[1]))
    if msg.quiet:
        print('\n'.join(importers))


def sanitychecks(arg, msg):
    """Sanity checks."""
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

    if arg.separator is None:
        configpath = os.path.join(os.environ.get('PASSWORD_STORE_DIR', ''),
                                  arg.root, '.import')
        if os.path.isfile(configpath):
            with open(configpath, 'r') as configfile:
                ini = configparser.ConfigParser()
                ini.read_file(configfile)
                arg.separator = ini.get('convert', 'separator', fallback='-')
        else:
            arg.separator = '-'

    return file


def report(arg, msg, paths):
    """Print final success report."""
    msg.success("Importing passwords from %s" % arg.manager)
    if arg.file is None:
        arg.file = 'read from stdin'
    msg.message("File: %s" % arg.file)
    if arg.root != '':
        msg.message("Root path: %s" % arg.root)
    msg.message("Number of password imported: %s" % len(paths))
    if arg.convert:
        msg.message("Forbidden chars converted")
        msg.message("Path separator used: %s" % arg.separator)
    if arg.clean:
        msg.message("Imported data cleaned")
    if arg.extra:
        msg.message("Extra data conserved")
    if paths:
        msg.message("Passwords imported:")
        paths.sort()
        for path in paths:
            msg.echo(os.path.join(arg.root, path))


def main(argv):
    arg = argumentsparse(argv)
    msg = Msg(arg.verbose, arg.quiet)

    if arg.list:
        listimporters(msg)
    else:
        file = sanitychecks(arg, msg)

        # Import and clean data
        ImporterClass = getattr(importlib.import_module(__name__),
                                importers[arg.manager][0])
        importer = ImporterClass(arg.extra, arg.separator)
        try:
            importer.parse(file)
            importer.clean(arg.clean, arg.convert)
        except (FormatError, AttributeError, ValueError):
            msg.die("%s is not a exported %s file" % (arg.file, arg.manager))
        except PermissionError as e:
            msg.die(e)
        finally:
            if arg.manager != 'networkmanager':
                file.close()

        # Insert data into the password store
        paths = []
        store = PasswordStore()
        if not store.exist():
            msg.die("password store not initialized")
        if not store.is_valid_recipients():
            msg.die('invalid user ID, password encryption aborted.')
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
            else:
                paths.append(passpath)

        # Success!
        report(arg, msg, paths)


if __name__ == "__main__":
    sys.argv.pop(0)
    main(sys.argv)
