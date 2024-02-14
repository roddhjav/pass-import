# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json
import os

from pass_import.core import register_managers
from pass_import.errors import FormatError, PMError
from pass_import.formats.cli import CLI
from pass_import.formats.csv import CSV
from pass_import.tools import getpassword


class LastpassCLI(CLI):
    """Importer & Exporter for Lastpass using lpass.

    Binary attachments are not supported by Lastpass
    The Lastpass login is given either by the prefix or by the configuration
    file under the lastpass.login entry.

    Example:
    -------
    .. code-block:: yml

        lastpass:
          login: <your email addresss>

    """
    name = 'lastpass'
    command = 'lpass'
    url = 'https://www.lastpass.com'
    himport = 'pass import lastpass <login>'
    keys = {
        'title': 'name',
        'login': 'username',
        'url': 'url',
        'comments': 'note',
        'group': 'group'
    }

    def __init__(self, prefix=None, settings=None):
        self._opt = []
        self.sep = '\\'

        settings = {} if settings is None else settings
        conf = settings.get('lastpass', {})
        prefix = conf.get('login', prefix)

        super().__init__(prefix, settings)
        self._setenv('LPASS_HOME')
        self._setenv('LPASS_AUTO_SYNC_TIME')
        self._setenv('LPASS_AGENT_TIMEOUT')
        self._setenv('LPASS_AGENT_DISABLE')
        self._setenv('LPASS_PINENTRY')
        self._setenv('LPASS_DISABLE_PINENTRY', value='1')
        self._setenv('LPASS_ASKPASS')
        self._setenv('LPASS_CLIPBOARD_COMMAND')

    def _path(self, path, rep=os.sep):
        r"""Lpass is not consitent with / and '\\'. Replace them by os.sep."""
        return path.replace('/', rep).replace(self.sep, rep)

    def sync(self):
        """Force a synchronization of the local cache with the servers."""
        self._command(['sync', '--color=never'])

    def list(self, path=''):
        """List the paths in the password store repository.

        :param str path: Root path to the password repository to list.
        :return list: Return a list of unique ID in the store.

        """
        uids = []
        path = path.replace(self.sep, os.sep)

        arg = ['ls', '--format=%ai|%aN', '--sync=now', '--color=never']
        data = self._command(arg).split('\n')
        for line in data:
            if '|' in line:
                uid, group = line.split('|', 1)
                group = group.replace(self.sep, os.sep)
                if not group.endswith(os.sep) and path in group:
                    uids.append(uid)
        return uids

    # Import methods

    def show(self, uid):
        """Decrypt a lastpass entry and read the credentials.

        lpass do not show the same data with the --json option and without.
        To retrieve the full entry, both --json and --format option need to
        be used.

        :param str uid: UniqueID to the password entry to decrypt.
        :return dict: Return a dictionary with of the password entry.

        """
        entry = {}

        # lpass show --json
        ignores = {'fullname'}
        keys = self.invkeys()
        jsons = self._command(['show', '--json', uid])
        item = json.loads(jsons).pop()
        for key, value in item.items():
            if key not in ignores:
                entry[keys.get(key, key)] = value
        entry['group'] = self._path(item['group'])

        # lpass show --format
        ignores = {'Username', 'Password', 'URL'}
        arg = ['show', '--color=never',
               "--format=%fn|%fv", '--color=never', uid]
        data = self._command(arg).split('\n')
        data.pop()
        data.pop(0)
        for line in data:
            if '|' in line:
                key, value = line.split('|', 1)
                if key not in ignores:
                    entry[key] = value

        # Special cleanup
        if entry.get('url', '') == 'http://':
            entry['url'] = ''
        return entry

    def parse(self):
        """Parse Lastpass repository using lpass."""
        uniqueids = self.list(self.root)
        if not uniqueids:
            raise FormatError('empty password store.')

        for uniqueid in uniqueids:
            entry = self.show(uniqueid)
            self.data.append(entry)

    # Export methods

    def remove(self, uid):
        """Move an entry to the Trash."""
        arg = ['rm', '--color=never', uid]
        self._command(arg)

    def insert(self, entry):
        """Insert a password entry into lastpass using lpass."""
        path = os.path.join(self.root, entry['path'])
        entry['group'] = os.path.dirname(path)
        entry['title'] = os.path.basename(path)
        path = entry['group'].replace(os.sep, self.sep) + '/' + entry['title']

        # Remove entries with the same name.
        uids = self.list(path)
        if uids:
            if not self.force:
                raise PMError(f"An entry already exists for {path}.")
            for uid in uids:
                self.remove(uid)

        # Insert the entry into lastpass
        seen = {'path', 'title', 'group'}
        exportkeys = {
            'title': 'Name',
            'password': 'Password',
            'login': 'Username',
            'url': 'URL',
            'comments': 'Notes',
        }
        data = ''
        for key in self.keyslist:
            if key in seen:
                continue
            if key in entry:
                data += f"{exportkeys.get(key, key)}: {entry[key]}\n"
            seen.add(key)

        if self.all:
            for key, value in entry.items():
                if key in seen:
                    continue
                data += f"{key}: {value}\n"

        arg = ['add', '--sync=now', '--non-interactive', '--color=never', path]
        self._command(arg, data)

    # Context manager methods

    def open(self):
        """Sign in to your Lastpass account."""
        if self.prefix == '':
            raise PMError("Your Lastpass username is empty")

        status = [self._binary, 'status', '--quiet']
        res, _, _ = self._call(status)
        if res:
            login = ['login', '--trust', '--color=never', self.prefix]
            password = getpassword('Lastpass')
            res = self._command(login, password)

    def close(self):
        """Synchronise and sign out of your Lastpass account."""
        self.sync()


class LastpassCSV(CSV):
    """Importer for Lastpass in CSV format."""
    name = 'lastpass'
    default = False
    url = 'https://www.lastpass.com'
    hexport = 'More Options > Advanced > Export'
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'extra',
        'group': 'grouping'
    }

    def parse(self):
        """Parse Lastpass CSV file."""
        super().parse()
        for entry in self.data:
            if 'group' in entry and entry['group'] is None:
                # LastPass will truncate everything after `$` in a
                # secure note entry when exporting as a CSV, including
                # any closing ", leaving the file in a corrupt
                # state. Triggering this is likely a symptom of such a
                # corrupted export.
                #
                # Likewise, it also has problems exporting single
                # quotes in the password field, causing all data prior
                # to the single quote (including the url field, etc.)
                # to be truncated, leading to the parser thinking the
                # path field wasn't included, and incorrectly
                # resulting in a value of None.
                raise FormatError(f'Invalid group in entry:\n{entry}.')
            entry['group'] = entry.get('group', '').replace('\\', os.sep)


register_managers(LastpassCLI, LastpassCSV)
