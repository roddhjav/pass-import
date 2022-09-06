# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import json
import os

from pass_import.core import register_managers
from pass_import.errors import PMError
from pass_import.formats.cli import CLI
from pass_import.formats.csv import CSV
from pass_import.formats.json import JSON
from pass_import.manager import PasswordImporter
from pass_import.tools import getpassword


class BitwardenCommon(PasswordImporter):
    """Common parsing methods across Bitwarden importers."""
    key_group = 'folders'
    key_group_id = 'folderId'  # Might need to check for both id anyways
    nesting_keys = {'card', 'identity'}
    ignore = {
        'login', 'id', 'folderId', 'collectionIds', 'organizationId', 'type',
        'favorite', 'secureNote'
    }

    def _sortgroup(self, folders):
        for entry in self.data:
            groupid = entry.get('group', '')
            entry['group'] = folders.get(groupid, '')

    @staticmethod
    def _parse_nested(destination_entry, nesting_source):
        for key, value in nesting_source.items():
            if key in destination_entry.keys():
                key = f'{key}_'
            if value:
                destination_entry[key] = value

    @staticmethod
    def _parse_custom_fields(destination_entry, custom_fields):
        for field in custom_fields:
            name = field['name']
            value = field['value']
            if name in destination_entry.keys():
                name = f'{name}_'
            if value:
                destination_entry[name] = value

    def _parse(self, folders, items):
        """Parse Bitwarden JSON structure."""
        keys = self.invkeys()
        folders_id = {}
        for item in folders:
            key = item.get('id', '')
            folders_id[key] = item.get('name', '')

        for item in items:
            entry = {}
            if 'folder' in self.key_group_id:
                entry['group'] = item.get(self.key_group_id, '')
            else:
                entry['group'] = item.get(self.key_group_id, [''])[0]
            logins = item.get('login', {})
            item.update(logins)
            for key, value in item.items():
                if key in self.ignore:
                    continue

                if key == 'fields':
                    self._parse_custom_fields(entry, value)
                elif key in self.nesting_keys:
                    self._parse_nested(entry, value)
                else:
                    if value:
                        entry[keys.get(key, key)] = value

            urls = entry.get('url')
            if urls:
                entry['url'] = urls[0]['uri']

                if len(urls) > 1:
                    index = 2
                    for url in urls[1:]:
                        entry[f'url{index}'] = url['uri']
                        index += 1

            self.data.append(entry)
        self._sortgroup(folders_id)


class BitwardenCLI(CLI, BitwardenCommon):
    """Importer & Exporter for Bitwarden using the CLI sdk 'bw'.

    :usage:
    The prefix is your bitwarden login email. If it is empty, it is read from
    the configuration file. Bitwarden server url, login are read from the
    configuration file.

    Alternatively, if the environment variable ``BW_SESSION`` is set to you
    current token, it will not sigin again.

    Attachment are not supported yet.

    Example:
    -------
    .. code-block:: yml

        bitwarden:
          login: <your email addresss>
          server: vault.bitwarden.com

    """
    name = 'bitwarden'
    command = 'bw'
    url = 'https://bitwarden.com'
    himport = 'pass import bitwarden <login>'
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'uris',
        'otpauth': 'totp',
        'comments': 'notes',
    }

    def __init__(self, prefix=None, settings=None):
        settings = {} if settings is None else settings
        conf = settings.get('bitwarden', {})
        prefix = conf.get('login', prefix)
        super().__init__(prefix, settings)
        if 'server' in conf:
            self._command(['config', 'server', conf['server']])

    # Import methods

    def parse(self):
        """Parse Bitwarden repository using bw."""
        self._parse(
            json.loads(self._command(['list', '--raw', 'folders'])),
            json.loads(self._command(['list', '--raw', 'items']))
        )

    # Export methods

    def sync(self):
        """Pull the latest vault data from server."""
        self._command(['sync', '--force'])

    def encode(self, data):
        """Encode the dictionary required to create an item."""
        return self._command(['encode'], json.dumps(data))

    @staticmethod
    def template():
        """Template for a new item object."""
        return {
            'organizationId': None,
            'folderId': None,
            'type': 1,
            'name': '',
            'notes': '',
            'favorite': False,
            'fields': [],
            'login': {},
            'secureNote': None,
            'card': None,
            'identity': None
        }

    def _folder(self, name):
        """Return a folder ID named after name. Create it it if needed."""
        arg = ['list', 'folders', f'--search={name}']
        folders = json.loads(self._command(arg))
        for folder in folders:
            if folder.get('name', '') == name:
                return folder['id']

        arg = ['create', 'folder']
        encoded = self.encode({'name': name})
        folder = json.loads(self._command(arg, encoded))
        return folder['id']

    def _setitem(self, folder, entry):
        """Convert a password entry into a bitwarden json dict."""
        seen = {'path', 'title', 'group', 'comments', 'url', 'password',
                'login', 'data'}

        item = self.template()
        item['folderId'] = folder
        for key in ['title', 'comments']:
            if key in entry:
                item[self.keys.get(key, key)] = entry[key]
        for key in ['login', 'password', 'otpauth']:
            item['login'][self.keys.get(key, key)] = entry.get(key, '')
        if 'url' in entry:
            item['login']['uris'] = [{
                'match': None,
                'uri': entry['url']
            }]

        if self.all:
            for key, value in entry.items():
                if key in seen:
                    continue
                item['fields'].append({
                    'name': self.keys.get(key, key),
                    'value': value,
                    'type': 0
                })

        return item

    def insert(self, entry):
        """Insert a password entry into bitwarden using bw."""
        path = os.path.join(self.root, entry['path'])
        entry['group'] = os.path.dirname(path)
        entry['title'] = os.path.basename(path)
        folderid = self._folder(entry['group'])

        # Ensure the entry is unique
        arg = ['list', 'items', f'--folderid={folderid}']
        entries = json.loads(self._command(arg))
        arg = ['create', 'item']
        for item in entries:
            if item.get('name', '') == entry['title']:
                if not self.force:
                    raise PMError(f"An entry already exists for {path}.")
                arg = ['edit', 'item', item['id']]
                break

        # Insert the entry into bitwarden
        encoded = self.encode(self._setitem(folderid, entry))
        res = self._command(arg, encoded)
        return json.loads(res).get('id', '')

    # Context manager methods

    def open(self):
        """Sign in to your Bitwarden account."""
        if self.prefix == '':
            raise PMError("Your Bitwarden username is empty")

        res = self._command(['status'])
        status = json.loads(res).get('status', '')
        if status == 'unlocked':
            return

        password = getpassword('bitwarden')
        if status == 'unauthenticated':
            if 'BW_CLIENTID' in os.environ:
                self._command(['login', '--apikey', '--raw'])
                token = self._command(['unlock', '--raw'], password)
            else:
                arg = ['login', '--raw', self.prefix]
                token = self._command(arg, password)

        elif status == 'locked':
            arg = ['unlock', '--raw']
            token = self._command(arg, password)

        else:
            raise PMError("Your Bitwarden login status is unkown")

        self.env['BW_SESSION'] = token

    def close(self):
        """Sign out of your 1Password account."""
        self._command(['sync', '--force'])


class BitwardenCSV(CSV):
    """Importer for Bitwarden in CSV format."""
    name = 'bitwarden'
    default = False
    url = 'https://bitwarden.com'
    hexport = 'Tools> Export Vault> File Format: .csv'
    himport = 'pass import bitwarden file.csv'
    keys = {
        'title': 'name',
        'password': 'login_password',
        'login': 'login_username',
        'url': 'login_uri',
        'comments': 'notes',
        'group': 'folder',
        'otpauth': 'login_totp',
    }


class BitwardenOrgCSV(BitwardenCSV):
    """Importer for Bitwarden in CSV format."""
    default = False
    keys = {
        'title': 'name',
        'password': 'login_password',
        'login': 'login_username',
        'url': 'login_uri',
        'comments': 'notes',
        'group': 'collections',
        'otpauth': 'login_totp',
    }


class BitwardenJSON(JSON, BitwardenCommon):
    """Importer for Bitwarden in JSON format."""
    name = 'bitwarden'
    default = False
    url = 'https://bitwarden.com'
    hexport = 'Tools> Export Vault> File Format: .json'
    himport = 'pass import bitwarden file.json'
    key_group = 'folders'
    key_group_id = 'folderId'
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'uris',
        'otpauth': 'totp',
        'comments': 'notes',
    }
    json_header = {
        'encrypted': False,
        'folders': [{
            'id': str,
            'name': str
        }],
        'items': [{
            'id': str,
            'folderId': str,
            'type': int,
            'name': str,
            'favorite': bool,
        }],
    }

    def parse(self):
        """Parse Bitwarden JSON file."""
        jsons = json.loads(self.file.read())
        self._parse(jsons.get(self.key_group, {}), jsons.get('items', {}))


class BitwardenOrgJSON(BitwardenJSON):
    """Importer for Bitwarden Organisation in JSON format."""
    key_group = 'collections'
    key_group_id = 'collectionIds'
    json_header = {
        'encrypted': False,
        'collections': list,
        'items': [{
            'id': str,
            'type': int,
            'name': str,
            'favorite': bool,
            'collectionIds': list,
        }],
    }


register_managers(BitwardenCLI, BitwardenCSV, BitwardenJSON,
                  BitwardenOrgCSV, BitwardenOrgJSON)
