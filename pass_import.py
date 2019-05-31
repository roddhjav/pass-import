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
import getpass
import argparse
import importlib
import configparser
from pathlib import Path
from datetime import datetime
from subprocess import Popen, PIPE  # nosec
from collections import defaultdict

__version__ = '2.6'

importers = {  # pylint: disable=invalid-name
    '1password': 'OnePassword',
    '1password4': 'OnePassword4',
    '1password4pif': 'OnePassword4PIF',
    'aegis': 'Aegis',
    'andotp': 'AndOTP',
    'apple-keychain': 'AppleKeychain',
    'bitwarden': 'Bitwarden',
    'buttercup': 'Buttercup',
    'chrome': 'Chrome',
    'chromesqlite': 'ChromeSQLite',
    'csv': 'CSV',
    'dashlane': 'Dashlane',
    'encryptr': 'Encryptr',
    'enpass': 'Enpass',
    'enpass6': 'Enpass6',
    'fpm': 'FigaroPM',
    'gnome-authenticator': 'GnomeAuthenticator',
    'gnome-keyring': 'GnomeKeyring',
    'gorilla': 'Gorilla',
    'kedpm': 'FigaroPM',
    'keepass': 'KeepassKDBX',
    'keepass-csv': 'KeepassCSV',
    'keepass-xml': 'KeepassXML',
    'keepassx': 'KeepassxXML',
    'keepassx2': 'Keepassx2KDBX',
    'keepassx2-csv': 'Keepassx2CSV',
    'keepassxc': 'KeepassxcKDBX',
    'keepassxc-csv': 'KeepassxcCSV',
    'keeper': 'Keeper',
    'lastpass': 'Lastpass',
    'networkmanager': 'NetworkManager',
    'myki': 'Myki',
    'pass': 'Pass',
    'passpie': 'Passpie',
    'passwordexporter': 'PasswordExporter',
    'pwsafe': 'Pwsafe',
    'revelation': 'Revelation',
    'roboform': 'Roboform',
    'upm': 'UPM',
}


class PasswordStoreError(Exception):
    """Error in the execution of password store."""


class FormatError(Exception):
    """Password importer format (CSV, XML, JSON or TXT) not recognized."""


class VersionError(Exception):
    """The python version is not a supported version."""


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
        """Verbose method, takes title and msg. msg can be empty."""
        if self.verb and msg == '':
            print("%s  .  %s%s%s%s" % (self.Bmagenta, self.end,
                                       self.magenta, title, self.end))
        elif self.verb:
            print("%s  .  %s%s%s: %s%s" % (self.Bmagenta, self.end,
                                           self.magenta, title, self.end, msg))

    def message(self, msg=''):
        """Message method."""
        if not self.quiet:
            print("%s  .  %s%s" % (self.Bold, self.end, msg))

    def echo(self, msg=''):
        """Echo message with after a tab."""
        if not self.quiet:
            print("\t%s" % msg)

    def success(self, msg=''):
        """Success method."""
        if not self.quiet:
            print("%s (*) %s%s%s%s" % (self.Bgreen, self.end,
                                       self.green, msg, self.end))

    def warning(self, msg=''):
        """Warning method."""
        if not self.quiet:
            print("%s  w  %s%s%s%s" % (self.Byellow, self.end,
                                       self.yellow, msg, self.end))

    def error(self, msg=''):
        """Error method."""
        print("%s [x] %s%sError: %s%s" % (self.Bred, self.end,
                                          self.Bold, self.end, msg))

    def die(self, msg=''):
        """Show an error and exit the program."""
        self.error(msg)
        exit(1)


try:
    import yaml
except ImportError:  # pragma: no cover
    err = Msg()  # pylint: disable=invalid-name
    err.die("pyaml is not present, you can install it with:\n"
            "  'sudo apt-get install python3-yaml', or\n"
            "  'pip3 install pyaml'")


class PasswordStore():
    """Simple Password Store wrapper for python.

    The constructor takes one optional parameter, the ``prefix``. Other pass
    settings are read from the environment variables. Furthermore, if
    ``prefix`` is not specified, the environment variable
    ``PASSWORD_STORE_DIR`` is required. The constructor will raise an exception
    if it is not present.

    This class supports all the environment variables supported by ''pass'',
    including ``GNUPGHOME``.

    This password store class works like this because it is mostly intended to
    be run in a pass extension, with pass settings available as environment
    variables. It does not intend to provide all the method available in pass
    but only the features required in pass extension.

    :param str prefix: Equivalent to `PASSWORD_STORE_DIR`.
    :param dict env: Environment variables used by `pass`.
    :raises PasswordStoreError: Error in the execution of password store.

    .. note::

        This password-store wrapper does not aim to be a full python
        implementation of pass. It requires pass as it calls it directly for
        all encryption operations. However, it aims to implement features in
        pure python when it is easier or/and more secure.

    """

    def __init__(self, prefix=None):
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
        self._setenv('PASSWORD_STORE_GENERATED_LENGTH', 'GENERATED_LENGTH')
        self._setenv('PASSWORD_STORE_CHARACTER_SET', 'CHARACTER_SET')
        self._setenv('PASSWORD_STORE_CHARACTER_SET_NO_SYMBOLS',
                     'CHARACTER_SET_NO_SYMBOLS')
        self._setenv('PASSWORD_STORE_ENABLE_EXTENSIONS')
        self._setenv('PASSWORD_STORE_EXTENSIONS_DIR', 'EXTENSIONS')
        self._setenv('PASSWORD_STORE_SIGNING_KEY')
        self._setenv('GNUPGHOME')

        if prefix:
            self.prefix = prefix
        if 'PASSWORD_STORE_DIR' not in self.env:
            raise PasswordStoreError("pass prefix unknown")

    def _setenv(self, var, env=None):
        """Add var in the environment variables dictionary."""
        if env is None:
            env = var
        if env in os.environ:
            self.env[var] = os.environ[env]

    def _call(self, command, data=None):
        """Call to a command."""
        nline = True
        if isinstance(data, bytes):
            nline = False
        with Popen(command, universal_newlines=nline, env=self.env, stdin=PIPE,
                   stdout=PIPE, stderr=PIPE, shell=False) as process:
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

    @property
    def prefix(self):
        """Get password store prefix from PASSWORD_STORE_DIR."""
        return self.env['PASSWORD_STORE_DIR']

    @prefix.setter
    def prefix(self, value):
        self.env['PASSWORD_STORE_DIR'] = value

    def insert(self, path, data, force=False):
        """Multiline insertion into the password store.

        :param str path: Path to insert into the password repository.
        :param str data: Data to insert into the password store.
        :param bool force: optional, Either or not to force the insert if the
            path already exist. Default: ``False``
        :raises PasswordStoreError: An entry already exists or in case of pass
            error.
        """
        if not force:
            if os.path.isfile(os.path.join(self.prefix, path + '.gpg')):
                raise PasswordStoreError("An entry already exists for %s."
                                         % path)
        arg = ['insert', '--multiline', '--force']
        arg.append(path)
        return self._pass(arg, data)

    def list(self, path=''):
        """List the paths in the password store repository.

        :param str path: Root path to the password repository to list.
        :return list: Return the list of paths in a store.

        """
        prefix = os.path.join(self.prefix, path)
        if os.path.isfile(prefix + '.gpg'):
            paths = [path]
        else:
            paths = []
            for ppath in Path(prefix).rglob('*.gpg'):
                file = os.sep + str(ppath)[len(self.prefix) + 1:]
                if "%s." % os.sep not in file:
                    file = os.path.splitext(file)[0][1:]
                    paths.append(file)
        paths.sort()
        return paths

    def show(self, path):
        """Decrypt path and read the credentials in the password file.

        :param str path: Path to the password entry to decrypt.
        :return dict: Return a dictionary with of the password entry.
        :raise PasswordStoreError: If path not in the store.
        """
        entry = dict()
        entry['group'] = os.path.dirname(path)
        entry['title'] = os.path.basename(path)
        data = self._pass(['show', path]).split('\n')
        data.pop()
        if data:
            line = data.pop(0)
            if ': ' in line:
                (key, value) = line.split(': ', 1)
                entry[key] = value
            else:
                entry['password'] = line
        for line in data:
            if ': ' in line:
                (key, value) = line.split(': ', 1)
                entry[key] = value
            elif line.startswith('otpauth://'):
                entry['otpauth'] = line
            elif 'comments' in entry:
                entry['comments'] += '\n' + line
        return entry

    def exist(self):
        """Check if the password store is initialized.

        :return bool:
            ``True`` if the password store is initialized, ``False`` otherwise.
        """
        return os.path.isfile(os.path.join(self.prefix, '.gpg-id'))

    def is_valid_recipients(self):
        """Ensure the GPG keyring is usable.

        This function ensures that:

        - All the public gpgids are present in the keyring.
        - At least one private key is present in the keyring.

        :return bool:
            ``True`` or ``False`` either or not the GPG keyring is usable.
        """
        with open(os.path.join(self.prefix, '.gpg-id'), 'r') as file:
            gpgids = file.read().split('\n')
            gpgids.pop()

        cmd = [self._gpgbinary, '--with-colons', '--batch', '--list-keys']
        for gpgid in gpgids:
            res, _, _ = self._call(cmd + [gpgid])
            if res:
                return False

        cmd = [self._gpgbinary, '--with-colons', '--batch',
               '--list-secret-keys']
        for gpgid in gpgids:
            res, _, _ = self._call(cmd + [gpgid])
            if res == 0:
                return True
        return False


class PasswordManager():
    """Common structure and methods for all password manager supported.

    Please read CONTRIBUTING.md for more details regarding data structure
    in pass-import.

    :param bool all: Etheir or not import all the data. Default: False
    :param str separator: Separator string. Default: '-'
    :param dict cleans: The list of string that should be cleaned by other
        string. Only enabled if the ``clean`` option is enabled.
    :param list protocols: The list of protocol. To be removed from the
        ``title`` key.
    :param list invalids: The list of invalid caracters. Replaced by the
        ``separator``.
    :param str cols: String that show the list of CSV expected columns to map
        columns to credential attributes. Only used for the CSV generic
        importer.

    To be used by classes that hinerit from PasswordManager.

    :param list[dict] data: The list of password entries imported by the parse
        method. Each password entry is a dictionary.
    :param list keyslist: The list of core key that will be present into the
        password entry even without the extra option.
    :param dict keys: Correspondence dictionary between the password-store key
        name (password, title, login...) and the key name from the password
        manager considered.
    :param format: Variable that check the format of the imported file.
        The type of this attribute depends of the importer type.

    :raises pass_import.FormatError:
        Password importer format (CSV, XML, JSON or TXT) not recognized.

    """
    keys = {}
    format = None
    keyslist = ['title', 'password', 'login', 'url', 'comments', 'otpauth',
                'group']

    def __init__(self, extra=False, separator='-', cleans=None,
                 protocols=None, invalids=None, cols=''):
        self.data = []
        self.all = extra
        self.separator = str(separator)
        self.cols = cols
        self.protocols = protocols if protocols else ['http://', 'https://']
        if cleans:
            self.cleans = cleans
        else:
            self.cleans = {" ": self.separator, "&": "and", "@": "At", "'": "",
                           "[": "", "]": "", "\t": ''}
        if invalids:
            self.invalids = invalids
        else:
            self.invalids = ['<', '>', ':', '"', '/', '\\', '|', '?', '*',
                             '\0']

    def get(self, entry):
        """Return the content of an entry in a password-store format.

        The entry is returned with the following format:

        .. code-block:: console

            <password>
            <key>: <value>

        If ``PasswordManager.all`` is true, all the entry values are printed.
        Otherwise only the key present in ``PasswordManager.keyslist`` are
        printed following the order from this list. The title, path and group
        keys are ignored.

        If the 'data' key is present, the entry is considered as a binary
        attachment and return the binary data.

        :param dict entry: The entry to print.
        :return str: A string with the entry data.
        :return byte: The binary content of the entry if it is a binary entry.
        """
        ignore = ['title', 'group', 'path']
        if 'data' in entry:
            return entry['data']
        string = entry.pop('password', '') + '\n'

        for key in self.keyslist:
            if key in ignore:
                continue
            if key in entry:
                if 'otpauth' in key:
                    string += "%s\n" % entry.pop(key)
                else:
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
        caracters = dict(zip(self.protocols, [''] * len(self.protocols)))
        return self._replaces(caracters, string)

    def _clean_group(self, string):
        """Remove invalids caracters in a group. Convert sep to os.sep."""
        caracters = dict(zip(self.invalids,
                             [self.separator] * len(self.invalids)))
        caracters['/'] = os.sep
        caracters['\\'] = os.sep
        return self._replaces(caracters, string)

    def _convert(self, string):
        """Convert invalid caracters by the separator in a string."""
        caracters = dict(zip(self.invalids,
                             [self.separator] * len(self.invalids)))
        return self._replaces(caracters, string)

    def _clean_title(self, string):
        """Clean the title from separator before addition to a path."""
        caracters = {'/': self.separator, '\\': self.separator}
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
                    entry['path'] = self._create_path(entry, path, clean,
                                                      convert)

    def _duplicate_numerise(self):
        """Add number to the remaining duplicated path."""
        seen = []
        for entry in self.data:
            path = entry.get('path', '')
            if path in seen:
                idx = 1
                while path in seen:
                    if re.search(r'%s(\d+)$' % self.separator, path) is None:
                        path += self.separator + str(idx)
                    else:
                        path = path.replace(self.separator + str(idx),
                                            self.separator + str(idx + 1))
                        idx += 1
                seen.append(path)
                entry['path'] = path
            else:
                seen.append(path)

    def _create_path(self, entry, path, clean, convert):
        """Create path from title and group."""
        title = ''
        for key in ['title', 'host', 'url', 'login']:
            if key in entry and entry[key]:
                title = entry[key]
                if key in ['title', 'host', 'url']:
                    title = self._clean_protocol(title)
                    # Only use hostname part of (potential) URLs
                    if key in ['host', 'url']:
                        for component in title.split('/'):
                            if component == '':
                                continue
                            else:
                                title = component
                                break
                title = self._clean_title(title)
                if clean:
                    title = self._clean_cmdline(title)
                if convert:
                    title = self._convert(title)
                if title != '':
                    if os.path.basename(path) != title:
                        path = os.path.join(path, title)
                        break

        if title == '' and os.path.basename(path) != 'notitle':
            path = os.path.join(path, 'notitle')
        entry.pop('title', '')
        return path

    def _invkeys(self):
        """Return the invert of self.keys."""
        return {v: k for k, v in self.keys.items()}

    def clean(self, clean, convert):
        """Clean parsed data in order to be imported to a store.

        **Features:**

        1. Remove unused keys and empty values.
        2. Clean protocol name in title.
        3. Clean group from unwanted value in Unix or Windows paths.
        4. Duplicate paths.

        :param bool clean:
            If ``True``, make the paths more command line friendly.
        :param bool convert:
            If ``True``, convert the invalid caracters present in the paths.

        """
        for entry in self.data:
            empty = [k for k, v in entry.items() if not v]
            for key in empty:
                entry.pop(key)

            path = self._clean_group(self._clean_protocol(entry.pop('group',
                                                                    '')))
            entry['path'] = self._create_path(entry, path, clean, convert)

        for i in range(2):
            self._duplicate_paths(clean, convert)
        self._duplicate_numerise()


class PasswordManagerCSV(PasswordManager):
    """Base class for CSV based importers.

    :param list fieldnames: The list of CSV field names

    """
    fieldnames = None

    def _checkline(self, file):
        """Ensure the first line of the CSV file is ``format``."""
        line = file.readline()
        if not line.startswith(self.format):
            raise FormatError()

    def _checkformat(self, fieldnames):
        """Ensure the CSV file has the same field than ``fieldnames``."""
        for csvkey in self.keys.values():
            if csvkey not in fieldnames:
                raise FormatError()

    def parse(self, file):
        """Parse CSV based file.

        :param io.IOBase file: File to parse

        """
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
    """Base class for XML based importers.

    :param str format: XML tag format.

    """

    def _checkformat(self, tree):
        """Ensure the root tree of the XML file has the correct format.

        This check is done by comparing the root tag with ```format``.
        """
        if tree.tag != self.format:
            raise FormatError()

    @classmethod
    def _getroot(cls, tree):
        return tree

    @classmethod
    def _getvalue(cls, element):
        return element.tag, element.text

    def _getentry(self, elements):
        entry = dict()
        keys = self._invkeys()
        for element in elements:
            xmlkey, value = self._getvalue(element)
            key = keys.get(xmlkey, xmlkey)
            entry[key] = value
        return entry

    def parse(self, file):
        """Parse XML based file. Requires defusedxml.

        :param io.IOBase file: File to parse

        """
        try:
            from defusedxml import ElementTree
        except ImportError as error:
            raise ImportError(error, name='defusedxml')
        tree = ElementTree.XML(file.read())
        self._checkformat(tree)
        root = self._getroot(tree)
        self._import(root)


class PasswordManagerJSON(PasswordManager):
    """Base class for JSON based importers."""

    def _sortgroup(self, folders):
        for folder in folders.values():
            parent = folder.get('parent', '')
            groupup = folders.get(parent, {}).get('group', '')
            folder['group'] = os.path.join(groupup, folder.get('group', ''))

        for entry in self.data:
            groupid = entry.get('group', '')
            entry['group'] = folders.get(groupid, {}).get('group', '')


class PasswordManagerYAML(PasswordManager):
    """Base class for YAML based importers.

    :param dict format: Dictionary that need to be present in the imported file
        to ensure the format is recognized.
    :param str rootkey: Root key where to find the data to import in the YAML.

    """
    rootkey = None

    def _checkformat(self, yamls):
        for key, value in self.format.items():
            if yamls.get(key, '') != value:
                raise FormatError()

    def parse(self, file):
        """Parse YAML based file.

        :param io.IOBase file: File to parse

        """
        yamls = yaml.safe_load(file)
        self._checkformat(yamls)

        keys = self._invkeys()
        for block in yamls[self.rootkey]:
            entry = dict()
            for key, value in block.items():
                if value:
                    entry[keys.get(key, key)] = value
            self.data.append(entry)


class PasswordManagerPIF(PasswordManagerJSON):
    """Base class for PIF based importers.

    :param list ignore: List of key in the PIF file to not try to import.

    """
    ignore = ['keyID', 'typeName', 'uuid', 'openContents', 'URLs']

    @staticmethod
    def _pif2json(file):
        """Convert 1pif to json: https://github.com/eblin/1passpwnedcheck."""
        data = file.read()
        cleaned = re.sub(r'(?m)^\*\*\*.*\*\*\*\s+', '', data)
        cleaned = cleaned.split('\n')
        cleaned = ','.join(cleaned).rstrip(',')
        cleaned = '[%s]' % cleaned
        return json.loads(cleaned)

    def parse(self, file):
        """Parse PIF based file.

        :param io.IOBase file: File to parse

        """
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
                    name = field.get('name', '')
                    designation = field.get('designation', '')
                    jsonkey = name or designation
                    key = keys.get(jsonkey, jsonkey)
                    entry[key] = field.get('value', '')

                item.update(scontent)
                for key, value in item.items():
                    if key not in self.ignore:
                        entry[keys.get(key, key)] = value
                self.data.append(entry)
        self._sortgroup(folders)


class PasswordManagerKDBX(PasswordManager):
    """Base class for KDBX based importers.

    :param list attributes: List of the attributes of PyKeePass to import.

    """
    keys = {'login': 'username', 'comments': 'notes', 'group': 'path'}
    attributes = ['title', 'username', 'password', 'url', 'notes', 'icon',
                  'tags', 'autotype_enabled', 'autotype_sequence', 'path',
                  'is_a_history_entry']

    def _getentry(self, kpentry):
        entry = dict()
        keys = self._invkeys()
        for attr in self.attributes:
            if hasattr(kpentry, attr):
                entry[keys.get(attr, attr)] = getattr(kpentry, attr)
        for key, value in kpentry.custom_properties.items():
            entry[key] = value
        return entry

    def parse(self, path):
        """Parse Keepass KDBX3 and KDBX4 files.

        Will ask for a password to unlock the data first. Support binary
        attachments.

        :param str path: Path to the KDBX file to parse.

        """
        try:
            from pykeepass import PyKeePass
        except ImportError as error:
            raise ImportError(error, name='pykeepass')

        password = getpass.getpass(prompt="Password for %s:" % path)
        with PyKeePass(path, password) as keepass:
            for kpentry in keepass.entries:
                entry = self._getentry(kpentry)
                entry['group'] = os.path.dirname(entry['group'])

                for hentry in kpentry.history:
                    history = self._getentry(hentry)
                    history['group'] = os.path.join('History', entry['group'])
                    self.data.append(history)

                for att in kpentry.attachments:
                    attachment = dict()
                    attachment['group'] = entry['group']
                    attachment['title'] = att.filename
                    attachment['data'] = att.data
                    self.data.append(attachment)
                    if entry.get('attachments', None):
                        entry['attachments'] += ", %s" % att.filename
                    else:
                        entry['attachments'] = att.filename
                self.data.append(entry)


class PasswordManagerOTP(PasswordManager):
    """Base class for OTP based importers."""

    @staticmethod
    def _otp(item):
        otp = "otpauth://%s/totp-secret?" % item.get('type', 'totp').lower()
        otp += "secret=%s&issuer=%s" % (item['secret'], item['label'])
        for setting in ['algorithm', 'digits', 'counter', 'period']:
            if setting in item:
                otp += "&%s=%s" % (setting, item[setting])
        return otp

    @classmethod
    def _read(cls, file):
        """Read file or data stream, return data."""
        return file.read()

    def parse(self, file):
        """Parse OTP based file.

        :param io.IOBase file: File to parse

        """
        jsons = json.loads(self._read(file))
        for item in jsons:
            entry = dict()
            entry['title'] = item['label']
            entry['otpauth'] = self._otp(item)

            for key in ['type', 'thumbnail', 'last_used']:
                entry[key] = str(item.get(key, '')).lower()
            entry['tags'] = ', '.join(item['tags'])
            self.data.append(entry)


class OnePassword4PIF(PasswordManagerPIF):
    """Importer for 1password 4 in PIF format.
    url: https://1password.com/
    export: See this [guide](https://support.1password.com/export/)
    import: pass import 1password4pif file.1pif
    """
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'location', 'comments': 'notesPlain', 'group': 'folderUuid'}


class OnePassword4(PasswordManagerCSV):
    """Importer for 1password 4 in CSV format.
    url: https://1password.com/
    export: See this [guide](https://support.1password.com/export)
    import: pass import 1password4 file.csv
    """
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'notes'}


class OnePassword(PasswordManagerCSV):
    """Importer for 1password 6 in CSV format.
    url: https://1password.com/
    export: See this [guide](https://support.1password.com/export/)
    import: pass import 1password file.csv
    """
    keys = {'title': 'Title', 'password': 'Password', 'login': 'Username',
            'url': 'URL', 'comments': 'Notes', 'group': 'Type'}


class Aegis(PasswordManagerOTP):
    """Importer for Aegis otp plain or encrypted JSON format.
    url: https://github.com/beemdevelopment/Aegis
    export: 'Settings> Tools: Export (Plain or encrypted)'
    import: pass import aegis file.json
    """

    @staticmethod
    def _decrypt(jsons, path):
        """Import file is AES GCM encrypted, let's decrypt it.

        Based on the import script from Aegis:
        https://github.com/beemdevelopment/Aegis/blob/master/scripts/decrypt.py
        Format documentation:
        https://github.com/beemdevelopment/Aegis/blob/master/docs/vault.md
        """
        try:
            import base64
            import cryptography
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
        except ImportError as error:
            raise ImportError(error, name='cryptography')

        password = getpass.getpass(prompt="Password for %s:" % path)

        master_key = None
        for slot in jsons['header']['slots']:
            if slot['type'] != 1:
                continue

            kdf = Scrypt(salt=bytes.fromhex(slot['salt']), length=32,
                         n=slot['n'], r=slot['r'], p=slot['p'],
                         backend=default_backend())
            key = kdf.derive(password.encode("utf-8"))

            cipher = AESGCM(key)
            param = slot['key_params']
            try:
                nonce = bytes.fromhex(param['nonce'])
                data = bytes.fromhex(slot['key']) + bytes.fromhex(param['tag'])
                master_key = cipher.decrypt(nonce=nonce, data=data,
                                            associated_data=None)
            except cryptography.exceptions.InvalidTag:  # pragma: no cover
                pass

        if master_key is None:  # pragma: no cover
            raise FormatError("unable to decrypt the master key.")

        cipher = AESGCM(master_key)
        param = jsons['header']['params']
        content = base64.b64decode(jsons['db']) + bytes.fromhex(param['tag'])
        plain = cipher.decrypt(nonce=bytes.fromhex(param['nonce']),
                               data=content, associated_data=None)
        return json.loads(plain.decode('utf-8'))

    def parse(self, file):
        """Parse Aegis exported file.

        Support both plain and encrypted export.

        :param io.IOBase file: File to parse

        """
        jsons = json.loads(self._read(file))
        try:
            if jsons['header']['slots'] is not None:
                jsons = self._decrypt(jsons, file.name)
            else:
                jsons = jsons['db']
        except Exception as error:
            raise FormatError(error)

        for item in jsons['entries']:
            entry = dict()
            info = item.pop('info', {})
            item.update(info)
            item['algorithm'] = item.pop('algo', None)
            entry['title'] = "%s%s" % (item['issuer'], item['name'])
            item['label'] = entry['title']
            entry['otpauth'] = self._otp(item)

            for key in ['group', 'type', 'icon']:
                entry[key] = str(item.get(key, '')).lower()
            self.data.append(entry)


class AndOTP(PasswordManagerOTP):
    """Importer for AndOTP plain or encrypted JSON format.
    url: https://github.com/andOTP/andOTP
    export: Backups> Backup plain, gpg or password encrypted
    import: pass import andotp file.{json, json.aes, gpg}
    """

    @classmethod
    def _read(cls, file):
        return file

    @staticmethod
    def _gpg_decrypt(data):
        """Import data is GPG encrypted, let's decrypt it."""
        gpgbinary = shutil.which('gpg2') or shutil.which('gpg')
        cmd = [gpgbinary, '--with-colons', '--batch', '--decrypt']
        with Popen(cmd, shell=False, universal_newlines=True, stdin=PIPE,
                   stdout=PIPE, stderr=PIPE) as process:
            (stdout, stderr) = process.communicate(data)
            if process.wait():  # pragma: no cover
                raise FormatError("%s %s" % (stderr, stdout))
            return stdout

    @staticmethod
    def _aes_decrypt(file):
        """Import file is AES GCM encrypted, let's decrypt it."""
        try:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError as error:
            raise ImportError(error, name='cryptography')
        else:
            path = file.name
        finally:
            file.close()

        password = getpass.getpass(prompt="Password for %s:" % path)
        with open(path, 'rb') as aesfile:
            data = aesfile.read()

        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(password.encode('UTF-8'))
        key = digest.finalize()

        cipher = AESGCM(key)
        data = cipher.decrypt(nonce=data[:12], data=data[12:],
                              associated_data=None)
        return data.decode('utf-8')

    def parse(self, file):
        """Parse AndOTP exported file.

        Support plain export, AES encrypted export and GPG encrypted export
        files.

        :param io.IOBase file: File to parse

        """
        try:
            data = file.read()
        except UnicodeDecodeError:
            data = self._aes_decrypt(file)
        else:
            if data.startswith('-----BEGIN PGP MESSAGE-----'):
                data = self._gpg_decrypt(data)
        super(AndOTP, self).parse(data)


class AppleKeychain(PasswordManager):
    """Importer for Apple Keychain.
    url: https://support.apple.com/guide/keychain-access
    export: See this [guide](https://gist.github.com/sangonz/601f4fd2f039d6ceb
        2198e2f9f4f01e0)
    import: pass import apple-keychain file.txt
    """
    keys = {'title': 7, 'login': 'acct', 'authentication_type': 'atyp',
            'creation_date': 'cdat', 'creator': 'crtr', 'description': 'desc',
            'alt_comment': 'crtr', 'modification_date': 'mdat',
            'password_path': 'path', 'protocol': 'ptcl', 'url': 'srvr',
            'security_domain': 'sdmn', 'service': 'svce'}

    @staticmethod
    def _keychain2yaml(file):
        """Convert keychain to yaml."""
        yamls = []
        data = file.read()
        caracters = {'data:\n': 'data: ', '<NULL>': '', r'<[\w]*>=': ': ',
                     '0x00000007 :': '0x00000007:', '0x00000008 :':
                     '0x00000008:', 'keychain: "([^"]*)"': '---'}
        for key in caracters:
            data = re.sub(key, caracters[key], data)
        data = data.strip('---').split('---')
        for block in data:
            yamls.append(yaml.safe_load(block))
        return yamls

    @staticmethod
    def _compose_url(entry):
        """Compose the URL from Apple non-standard protocol names."""
        sub = {'htps': 'https', 'ldps': 'ldaps', 'ntps': 'nntps',
               'sox': 'socks', 'teln': 'telnet', 'tels': 'telnets',
               'imps': 'imaps', 'pops': 'pop3s'}
        url = entry.get('url', '')
        protocol = entry.get('protocol', '')
        if url and protocol:
            url = "%s://%s" % (sub.get(protocol, protocol), url.strip())
        return url

    @staticmethod
    def _human_date(date):
        """Return the date in human readable format."""
        try:
            if date[-1:] == '\x00':
                date = date[:-1]
            thedate = datetime.strptime(date, '%Y%m%d%H%M%SZ')
            return str(thedate)
        except (ValueError, UnicodeError):  # pragma: no cover
            return date

    @staticmethod
    def _decode(string):
        """Extract and decode hexadecimal value from a string."""
        hexmod = re.findall(r'0x[0-9A-F]*', string)
        if hexmod:
            return bytes.fromhex(hexmod[0][2:]).decode('utf-8')
        return string

    def _decode_data(self, entry):
        """Decode data field (password or comments)."""
        try:
            from defusedxml import ElementTree
        except ImportError as error:
            raise ImportError(error, name='defusedxml')

        key = entry.get('type', 'password')
        key = 'comments' if key == 'note' else key
        data = entry.pop('data', '')
        if isinstance(data, int):
            return key, ''

        data = self._decode(data)
        if key == 'comments':
            if data:
                try:
                    tree = ElementTree.XML(data)
                except ElementTree.ParseError:
                    return key, ''

                found = tree.find('.//string')
                if found is None:
                    return key, ''
                return key, found.text
            return key, ''
        return key, data

    def parse(self, file):
        """Parse apple-keychain format by converting it in yaml first.

        Requires python3-defusedxml due to internal XML string to decode.

        :param io.IOBase file: File to parse

        """
        yamls = self._keychain2yaml(file)
        keys = self._invkeys()
        for block in yamls:
            entry = dict()
            attributes = block.pop('attributes', {})
            block.update(attributes)
            for key, value in block.items():
                if value is not None:
                    entry[keys.get(key, key)] = value

            key, value = self._decode_data(entry)
            entry[key] = value
            entry['url'] = self._compose_url(entry)
            for key in ['creation_date', 'modification_date']:
                entry[key] = self._human_date(self._decode(entry.get(key, '')))

            self.data.append(entry)


class Bitwarden(PasswordManagerCSV):
    """Importer for Bitwarden in CSV format.
    url: https://bitwarden.com/
    export: 'Tools: Export'
    import: pass import bitwarden file.csv
    """
    keys = {'title': 'name', 'password': 'login_password',
            'login': 'login_username', 'url': 'login_uri', 'comments': 'notes',
            'group': 'folder'}


class Buttercup(PasswordManagerCSV):
    """Importer for Buttercup in CSV format.
    url: https://buttercup.pw/
    export: File > Export > Export File to CSV
    import: pass import buttercup file.csv
    """
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'URL', 'comments': 'Notes', 'group': '!group_name'}
    ignore = ['!group_id', 'id']

    def parse(self, file):
        super(Buttercup, self).parse(file)
        for entry in self.data:
            for key in self.ignore:
                entry.pop(key, None)


class Chrome(PasswordManagerCSV):
    """Importer for Chrome in CSV format.
    url: https://support.google.com/chrome
    export: See this [guide](https://www.axllent.org/docs/view/export-chrome-
        passwords/)
    import: pass import chrome file.csv
    """
    keys = {'title': 'name', 'password': 'password', 'login': 'username',
            'url': 'url'}


class ChromeSQLite(PasswordManagerCSV):
    """Importer for Chrome SQLite in CSV format.
    url: https://support.google.com/chrome
    export: See this [guide](https://www.axllent.org/docs/view/export-chrome-
        passwords/)
    import: pass import chromesqlite file.csv
    """
    keys = {'title': 'display_name', 'password': 'password_value',
            'login': 'username_value', 'url': 'origin_url'}


class CSV(PasswordManagerCSV):
    """Importer in generic CSV format.
    url: ''
    export: 'generic csv importer'
    import: pass import csv file.csv --cols 'url,login,,password'
    extra: >-
        You should use the --cols option to map columns to credential
        attributes.

        The recognized column names by pass-import are the following:
            'title', 'password', 'login', 'url', 'comments', 'otpauth', 'group'
        ``password`` will be the first line of the password entry. ``title``
        and ``group`` field are used to generate the password path. If you
        have otp data, they should be named as ``otpauth``. These are the
        *standard* field names. You can add any other field you want.

    """

    def parse(self, file):
        file.readline()
        if ',' in self.cols:
            self.fieldnames = self.cols.split(',')
        else:
            raise FormatError("no columns to map to credential attributes.")
        super(CSV, self).parse(file)


class Dashlane(PasswordManagerCSV):
    """Importer for Dashlane in CSV format.
    url: https://www.dashlane.com/
    export: File > Export > Unsecured Archive in CSV
    import: pass import dashlane file.csv
    """
    fieldnames = ['title', 'url', 'login', 'password', 'comments']
    keys = {'title': 'title', 'password': 'password', 'login': 'login',
            'url': 'url', 'comments': 'comments'}


class Encryptr(PasswordManagerCSV):
    """Importer for Encryptr in CSV format.
    url: https://spideroak.com/encryptr/
    export: Compile from source and follow instructions from this [guide](htt
        ps://github.com/SpiderOak/Encryptr/issues/295#issuecomment-322449705)
    import: pass import encryptr file.csv
    """
    keys = {'title': 'Label', 'password': 'Password', 'login': 'Username',
            'url': 'Site URL', 'comments': 'Notes', 'text': 'Text'}

    @classmethod
    def _checkformat(cls, fieldnames):
        for csvkey in ("Entry Type", "Label", "Notes"):
            if csvkey not in fieldnames:
                raise FormatError()


class Enpass(PasswordManagerCSV):
    """Importer for Enpass in CSV format.
    url: https://www.enpass.io/
    export: File > Export > As CSV
    import: pass import enpass file.csv
    """
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
            while index + 2 <= len(row):
                key = keys.get(row[index], row[index])
                entry[key] = row[index + 1]
                index += 2

            self.data.append(entry)


class Enpass6(PasswordManagerJSON):
    """Importer for Enpass 6 in CSV format.
    url: https://www.enpass.io/
    export: Menu > File > Export > As JSON
    import: pass import enpass6 file.json
    """
    keyslist = ['title', 'password', 'login', 'url', 'comments', 'group',
                'email']
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'website', 'comments': 'note', 'group': 'group',
            'email': 'e-mail'}
    ignore = ['fields', 'folders', 'icon']

    def parse(self, file):
        """Parse Enpass 6 JSON file.

        :param io.IOBase file: File to parse

        """
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
    """Importer for Figaro Password Manager in XML format.
    url: http://fpm.sourceforge.net/
    export: 'File > Export Passwords: Plain XML'
    import: pass import fpm file.xml
    """
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
    """Importer for Gorilla in CSV format.
    url: https://github.com/zdia/gorilla/wiki
    export: 'File > Export: Yes: CSV Files'
    import: pass import gorilla file.csv
    """
    keys = {'title': 'title', 'password': 'password', 'login': 'user',
            'url': 'url', 'comments': 'notes', 'group': 'group'}

    def parse(self, file):
        super(Gorilla, self).parse(file)
        for entry in self.data:
            group = re.sub(r'(?<=[^\\])\.', os.sep, entry.get('group', ''))
            entry['group'] = re.sub(r'\\.', '.', group)


class GnomeAuthenticator(PasswordManagerOTP):
    """Importer for Gnome Authenticator in JSON format.
    url: https://gitlab.gnome.org/World/Authenticator
    export: Backup > in a plain-text JSON file
    import: pass import gnome-authenticator json.csv
    """


class GnomeKeyring(PasswordManager):
    """Importer for Gnome Keyring.
    url: https://wiki.gnome.org/Projects/GnomeKeyring
    export: Nothing to do
    import: pass import gnome-keyring
    """
    keys = {'login': 'account', 'url': 'host'}

    def parse(self, label):
        """Direct import from the Gnome keyring using Dbus.

        :param str label: The collection label to import. If empty string
            import all collection.

        """
        if sys.version_info.minor < 5:
            raise VersionError('gnome keyring import requires python 3.5+')
        try:
            import secretstorage
        except ImportError as error:
            raise ImportError(error, name='secretstorage')

        keys = self._invkeys()
        connection = secretstorage.dbus_init()
        for collection in secretstorage.get_all_collections(connection):
            group = collection.get_label()
            if label not in ('', group):
                continue

            collection.unlock()
            for item in collection.get_all_items():
                entry = dict()
                entry['group'] = group
                entry['title'] = item.get_label()
                entry['password'] = item.get_secret().decode('utf-8')
                entry['modified'] = item.get_modified()
                entry['created'] = item.get_created()
                for key, value in item.get_attributes().items():
                    entry[keys.get(key, key)] = value
                self.data.append(entry)


class KeepassKDBX(PasswordManagerKDBX):
    """Importer for Keepass encrypted KDBX format.
    url: https://www.keepass.info
    export: Nothing to do
    import: pass import keepass file.kdbx
    """


class KeepassxXML(PasswordManagerXML):
    """Importer for KeepassX in XML format.
    url: https://www.keepassx.org/
    export: File > Export to > Keepass XML File
    import: pass import keepassx file.xml
    """
    group = 'group'
    entry = 'entry'
    format = 'database'
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'comment'}

    @classmethod
    def _getpath(cls, element, path=''):
        title = ''
        if element.tag != 'database':
            if element.find('title').text:
                title = element.find('title').text
        return os.path.join(path, title)

    def _import(self, element, path=''):
        path = self._getpath(element, path)
        for group in element.findall(self.group):
            self._import(group, path)
        for xmlentry in element.findall(self.entry):
            entry = self._getentry(xmlentry)
            entry['group'] = path
            self.data.append(entry)


class KeepassXML(KeepassxXML):
    """Importer for Keepass in XML format.
    url: https://www.keepass.info
    export: File > Export > Keepass2 (XML)
    import: pass import keepass-xml file.xml
    """
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
    def _getpath(cls, element, path=''):
        """Generate path name from elements title and current path."""
        title = ''
        if element.tag == 'Group':
            title = element.find('Name').text
        if title is None:
            title = ''
        return os.path.join(path, title)

    @classmethod
    def _getvalue(cls, element):
        xmlkey = value = ''
        for child in element.findall('Key'):
            xmlkey = child.text
            value = element.find('Value').text
        return xmlkey, value


class KeepassCSV(PasswordManagerCSV):
    """Importer for Keepass in CSV format.
    url: https://www.keepass.info
    export: File > Export > Keepass (CSV)
    import: pass import keepass-csv file.csv
    """
    keys = {'title': 'Account', 'password': 'Password', 'login': 'Login Name',
            'url': 'Web Site', 'comments': 'Comments'}


class Keepassx2KDBX(PasswordManagerKDBX):
    """Importer for KeepassX2 encrypted KDBX format.
    url: https://www.keepassx.org/
    export: Nothing to do
    import: pass import keepassx2 file.kdbx
    """


class Keepassx2CSV(PasswordManagerCSV):
    """Importer for KeepassX2 in CSV format.
    url: https://www.keepassx.org/
    export: Database > Export to CSV File
    import: pass import keepassx2-csv file.csv
    """
    keys = {'title': 'Title', 'password': 'Password', 'login': 'Username',
            'url': 'URL', 'comments': 'Notes', 'group': 'Group'}


class KeepassxcKDBX(PasswordManagerKDBX):
    """Importer for KeepassXC encrypted KDBX format.
    url: https://keepassxc.org/
    export: Nothing to do
    import: pass import keepassxc file.kdbx
    """


class KeepassxcCSV(Keepassx2CSV):
    """Importer for KeepassXC in CSV format.
    url: https://keepassxc.org/
    export: Database > Export to CSV File
    import: pass import keepassxc-csv file.csv
    """


class Keeper(PasswordManagerCSV):
    """Importer for Keeper in CSV format.
    url: https://keepersecurity.com/
    export: 'Settings > Export : Export to CSV File'
    import: pass import keeper file.csv
    """
    fieldnames = ['group', 'title', 'login', 'password', 'url', 'comments']
    keys = {'title': 'title', 'password': 'password', 'login': 'login',
            'url': 'url', 'comments': 'comments', 'group': 'group'}


class Lastpass(PasswordManagerCSV):
    """Importer for Lastpass in CSV format.
    url: https://www.lastpass.com/
    export: More Options > Advanced > Export
    import: pass import lastpass file.csv
    """
    keys = {'title': 'name', 'password': 'password', 'login': 'username',
            'url': 'url', 'comments': 'extra', 'group': 'grouping'}

    def parse(self, file):
        super(Lastpass, self).parse(file)
        for entry in self.data:
            entry['group'] = entry.get('group', '').replace('\\', os.sep)


class NetworkManager(PasswordManager):
    """Importer for Network Manager.
    url: https://wiki.gnome.org/Projects/NetworkManager
    export: Also support specific networkmanager dir and ini file
    import: pass import networkmanager
    extra: |-
        Support import from the installed network configuration but also
        from specific directory of  networkmanger configuration file and from
        given file.

        From directory of ini file: pass import networkmanager dir/

        From ini file: pass import networkmanager file.ini

    """
    default = '/etc/NetworkManager/system-connections'
    keyslist = ['title', 'password', 'login', 'ssid']
    keys = {'title': 'connection.id', 'password': 'wifi-security.psk',
            'login': '802-1x.identity', 'ssid': 'wifi.ssid'}

    def parse(self, data):
        """Parse NetworkManager ini config file or directory.

        :param str data: If ``data`` is file object, import file data. If
            ``data`` is a path to a file, open it and import the data. If
            ``data`` is a path to a directory, open the files it contains and
            import all the files. If ```data`` is '' import data from the
            default directory.

        """
        if isinstance(data, io.IOBase):
            files = [data]
        else:
            data = self.default if data == '' else data
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
                    entry[keys.get(inikey, inikey)] = ini.get(section, option,
                                                              fallback='')

            if entry.get('password', None) is not None:
                self.data.append(entry)

            file.close()


class Myki(PasswordManagerCSV):
    """Importer for Myki in CSV format.
    url: https://myki.com/
    export: See this [guide](https://support.myki.com/myki-app/exporting-your
        -passwords-from-the-myki-app/how-to-export-your-passwords-account-data
        -from-myki)
    import: pass import myki file.csv
    """
    keys = {'title': 'Name', 'password': 'Password', 'login': 'Username',
            'url': 'Url', 'comments': 'Extra', 'group': 'Grouping'}


class Pass(PasswordManager):
    """Importer for password-store.
    url: https://passwordstore.org
    export: Nothing to do
    import: pass import pass path/to/store
    """

    def parse(self, prefix):
        """Parse a password-store repository.

        :param str prefix: prefix is is the path to the pass repo

        """
        store = PasswordStore(prefix)
        if not store.exist():  # pragma: no cover
            raise FormatError('no password store to import.')
        if not store.is_valid_recipients():  # pragma: no cover
            raise FormatError('invalid user ID, password encryption aborted.')

        paths = store.list()
        if not paths:
            raise FormatError('empty password store.')  # pragma: no cover
        for path in paths:
            try:
                entry = store.show(path)
            except PasswordStoreError as error:  # pragma: no cover
                raise FormatError(error)
            self.data.append(entry)


class Passpie(PasswordManagerYAML):
    """Importer for Passpie in YAML format.
    url: https://passpie.readthedocs.io
    export: '`passpie export file.yml`'
    import: pass import passpie file.yml
    """
    rootkey = 'credentials'
    format = {'handler': 'passpie', 'version': 1.0}
    keys = {'title': 'name', 'password': 'password', 'login': 'login',
            'comments': 'comment'}


class PasswordExporter(PasswordManagerCSV):
    """Importer for Firefox password exporter extension in CSV format.
    url: https://github.com/kspearrin/ff-password-exporter
    export: 'Add-ons Prefs: Export Passwords: CSV'
    import: pass import passwordexporter file.csv
    """
    keys = {'title': 'hostname', 'password': 'password', 'login': 'username'}


class Pwsafe(PasswordManagerXML):
    """Importer for Pwsafe in XML format.
    url: https://pwsafe.org/
    export: File > Export To > XML Format
    import: pass import pwsafe file.xml
    """
    format = 'passwordsafe'
    keyslist = ['title', 'password', 'login', 'url', 'email', 'comments',
                'group']
    keys = {'title': 'title', 'password': 'password', 'login': 'username',
            'url': 'url', 'email': 'email', 'comments': 'notes',
            'group': 'group'}

    def _import(self, element):
        delimiter = element.attrib['delimiter']
        for xmlentry in element.findall('entry'):
            entry = self._getentry(xmlentry)
            entry['group'] = entry.get('group', '').replace('.', os.sep)
            entry['comments'] = entry.get('comments', '').replace(delimiter,
                                                                  '\n')
            histkey = './pwhistory/history_entries/history_entry'
            for historyentry in xmlentry.findall(histkey):
                for hist in historyentry:
                    xmlkey, value = self._getvalue(hist)
                    xmlkey += historyentry.attrib.get('num', '')
                    entry[xmlkey] = value
            self.data.append(entry)


class Revelation(PasswordManagerXML):
    """Importer for Revelation in XML format.
    url: https://revelation.olasagasti.info/
    export: 'File > Export: XML'
    import: pass import revelation file.xml
    """
    format = 'revelationdata'
    keys = {'title': 'name', 'password': 'generic-password',
            'login': 'generic-username', 'url': 'generic-hostname',
            'comments': 'notes', 'group': '', 'description': 'description'}

    @classmethod
    def _getvalue(cls, element):
        key = element.tag
        if key == 'field':
            key = element.attrib.get('id', '')
        return key, element.text

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
    """Importer for Roboform in CSV format.
    url: https://www.roboform.com/
    export: 'Roboform > Options > Data & Sync > Export To: CSV file'
    import: pass import roboform file.csv
    """
    keys = {'title': 'Name', 'password': 'Pwd', 'login': 'Login', 'url': 'Url',
            'comments': 'Note', 'group': 'Folder'}


class UPM(PasswordManagerCSV):
    """Importer for Universal Password Manager (UPM) in CSV format.
    url: http://upm.sourceforge.net/
    export: Database > Export
    import: pass import upm file.csv
    """
    fieldnames = ['title', 'login', 'password', 'url', 'comments']
    keys = {'title': 'title', 'password': 'password', 'login': 'login',
            'url': 'url', 'comments': 'comments'}


def argumentsparse():
    """Geting arguments for 'pass import'."""
    parser = argparse.ArgumentParser(prog='pass import', description="""
  Import data from most of the password manager. Passwords
  are imported in the existing default password store, therefore
  the password store must have been initialised before with 'pass init'""",
    formatter_class=argparse.RawDescriptionHelpFormatter,  # noqa
    epilog="More information may be found in the pass-import(1) man page.")

    parser.add_argument('manager', type=str, nargs='?', default='',
                        help="Can be: %s" % ', '.join(importers) + '.')
    parser.add_argument('file', type=str, nargs='?', default='',
                        help="""Path to the file or directory that contains the
                        data to import. Can also be a label.""")

    parser.add_argument('-p', '--path', action='store', dest='root',
                        default='', metavar='PATH',
                        help='Import the passwords to a specific subfolder.')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Also import all the extra data present.')
    parser.add_argument('-c', '--clean', action='store_true',
                        help='Make the paths more command line friendly.')
    parser.add_argument('-C', '--convert', action='store_true',
                        help='Convert invalid caracters present in the paths.')
    parser.add_argument('-s', '--sep', action='store', dest='separator',
                        metavar='CAR',
                        help="""Provide a caracter of replacement for the path
                         separator. Default: '-' """)
    parser.add_argument('--cols', action='store', default='',
                        help='CSV expected columns to map columns to '
                             'credential attributes. Only used for the generic'
                             ' csv importer.')
    parser.add_argument('--config', action='store', default='',
                        help="Set a config file. Default: '.import'")
    parser.add_argument('-l', '--list', action='store_true',
                        help='List the supported password managers.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Overwrite existing path.')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __version__,
                        help='Show the program version and exit.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet', action='store_true', help='Be quiet.')
    group.add_argument('-v', '--verbose', action='store_true',
                       help='Be verbose.')

    return parser


def getdoc(importer):
    """Read importer class docstring and retrieve importer meta."""
    # pylint: disable=invalid-name
    ImporterClass = getattr(importlib.import_module(__name__),  # noqa
                            importers[importer])
    docstring = ImporterClass.__doc__.split('\n')
    doc = {'title': docstring.pop(0)}
    doc.update(yaml.safe_load('\n'.join(docstring)))
    return doc


def listimporters(msg):
    """List supported password managers."""
    msg.success("The %s supported password managers are:" % len(importers))
    if msg.quiet:
        print('\n'.join(importers))
    else:
        for importer in sorted(importers):
            doc = getdoc(importer)
            msg.message("%s%-21s%s%s" % (msg.Bold, importer, msg.end,
                                         doc['url']))
    exit(0)


class Settings(dict):
    """Settings dictionary with specific merge method."""

    def merge(self, other):
        """Update the dictionary only if the value is not null."""
        for key, value in other.items():
            if value is not None:
                self[key] = value


def getsettings(arg):
    """Generate settings merged from args, config file and default.

    Order of presedance of the settings:
    1. Program options,
    2. Config file,
    3. Default values.

    """
    defaults = {'separator': '-',
                'cleans': {" ": '-', "&": "and", "@": "At", "'": "",
                           "[": "", "]": "", "\t": ''},
                'protocols': ['http://', 'https://'],
                'invalids': ['<', '>', ':', '"', '/', '\\', '|', '?', '*',
                             '\0']}
    settings = Settings(defaults)
    configs = {}

    if os.path.isfile(arg['config']):
        configpath = arg['config']
    else:
        configpath = os.path.join(os.environ.get('PASSWORD_STORE_DIR', ''),
                                  arg.get('root', ''), '.import')

    if os.path.isfile(configpath):
        with open(configpath, 'r') as file:
            configs = yaml.safe_load(file)
    settings.merge(configs)
    settings.merge(arg)
    settings['cleans'][' '] = settings['separator']
    return settings


def sanitychecks(arg, msg):
    """Sanity checks."""
    if arg['manager'] == '':
        msg.die("password manager not present. See 'pass import -h'")
    if arg['manager'] not in importers:
        msg.die("%s is not a supported password manager" % arg['manager'])

    # File opened by the importer
    pathonly = ('keepass', 'keepassxc', 'keepassx2', 'google-authenticator')
    if arg['manager'] in pathonly and os.path.isfile(arg['file']):
        file = arg['file']

    # Ini file import or dir of ini file or default dir
    elif arg['manager'] == 'networkmanager' and (
            arg['file'] == '' or os.path.isdir(arg['file'])):
        file = arg['file']

    # Direct import from the keyring using Dbus
    elif arg['manager'] == 'gnome-keyring':
        file = arg['file']

    # File is is the path to the pass repo
    elif arg['manager'] == 'pass' and os.path.isdir(arg['file']):
        file = arg['file']

    # Default: open the file
    elif os.path.isfile(arg['file']):
        encoding = 'utf-8'
        if arg['manager'] == '1password4pif':
            encoding = 'utf-8-sig'
        file = open(arg['file'], 'r', encoding=encoding)
    else:
        msg.die("%s is not a file" % arg['file'])

    return file


def report(arg, msg, paths):
    """Print final success report."""
    msg.success("Importing passwords from %s" % arg['manager'])
    msg.message("File: %s" % arg['file'])
    if arg['root'] != '':
        msg.message("Root path: %s" % arg['root'])
    msg.message("Number of password imported: %s" % len(paths))
    if arg['convert']:
        msg.message("Forbidden chars converted")
        msg.message("Path separator used: %s" % arg['separator'])
    if arg['clean']:
        msg.message("Imported data cleaned")
    if arg['all']:
        msg.message("All data imported")
    if paths:
        msg.message("Passwords imported:")
        paths.sort()
        for path in paths:
            msg.echo(os.path.join(arg['root'], path))


def main(argv):
    """pass-import main function."""
    arg = vars(argumentsparse().parse_args(argv))
    msg = Msg(arg['verbose'], arg['quiet'])
    try:
        arg = getsettings(arg)
    except AttributeError as error:
        msg.verbose(error)
        msg.die("configuration file not valid.")

    if arg['list']:
        listimporters(msg)
    file = sanitychecks(arg, msg)

    # Import and clean data. pylint: disable=invalid-name
    ImporterClass = getattr(importlib.import_module(__name__),  # noqa
                            importers[arg['manager']])
    importer = ImporterClass(arg['all'], arg['separator'], arg['cleans'],
                             arg['protocols'], arg['invalids'], arg['cols'])
    try:
        importer.parse(file)
        importer.clean(arg['clean'], arg['convert'])
    except (yaml.scanner.ScannerError,
            FormatError, AttributeError, ValueError) as error:
        msg.warning(error)
        msg.die("%s is not a valid exported %s file." % (arg['file'],
                                                         arg['manager']))
    except ImportError as error:
        msg.verbose(error)
        msg.die("Importing %s, missing required dependency: %s\n"
                "You can install it with:\n"
                "  'sudo apt-get install python3-%s', or\n"
                "  'pip3 install %s'" % (arg['manager'], error.name,
                                         error.name, error.name))
    except (PermissionError, VersionError) as error:  # pragma: no cover
        msg.die(error)
    finally:
        if arg['manager'] not in ('networkmanager', 'keepass', 'keepassxc',
                                  'keepassx2', 'pass', 'gnome-keyring',
                                  'google-authenticator'):
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
            passpath = os.path.join(arg['root'], entry['path'])
            data = importer.get(entry)
            msg.verbose("Path", passpath)
            if not isinstance(data, bytes):
                msg.verbose("Data", data.replace('\n', '\n           '))
            store.insert(passpath, data, arg['force'])
        except PasswordStoreError as error:
            msg.warning("Impossible to insert %s into the store: %s"
                        % (passpath, error))
        else:
            paths.append(passpath)

    # Success!
    report(arg, msg, paths)


if __name__ == "__main__":
    sys.argv.pop(0)
    main(sys.argv)
