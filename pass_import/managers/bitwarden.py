# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import json

from pass_import.core import register_managers
from pass_import.formats.csv import CSV
from pass_import.formats.json import JSON


class BitwardenCSV(CSV):
    """Importer for Bitwarden in CSV format."""
    name = 'bitwarden'
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


class BitwardenJSON(JSON):
    """Importer for Bitwarden in JSON format."""
    name = 'bitwarden'
    default = False
    url = 'https://bitwarden.com'
    hexport = 'Tools> Export Vault> File Format: .json'
    himport = 'pass import bitwarden file.json'
    ignore = {'login', 'id', 'folderId', 'secureNote', 'type', 'favorite'}
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'uris',
        'otpauth': 'totp',
        'comments': 'notes',
    }
    json_header = {
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

    def _sortgroup(self, folders):
        for entry in self.data:
            groupid = entry.get('group', '')
            entry['group'] = folders.get(groupid, '')

    def parse(self):
        """Parse Bitwarden JSON file."""
        jsons = json.loads(self.file.read())
        keys = self.invkeys()
        folders = dict()
        for item in jsons.get('folders', {}):
            key = item.get('id', '')
            folders[key] = item.get('name', '')

        for item in jsons.get('items', {}):
            entry = dict()
            entry['group'] = item.get('folderId', '')
            logins = item.get('login', {})
            item.update(logins)
            for key, value in item.items():
                if key not in self.ignore:
                    entry[keys.get(key, key)] = value

            entry['url'] = entry.get('url', [{}])[0].get('uri', '')
            self.data.append(entry)
        self._sortgroup(folders)


register_managers(BitwardenCSV, BitwardenJSON)
