# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json
import re
from pass_import.core import register_managers, register_detecters
from pass_import.formats.csv import CSV
from pass_import.formats.json import JSON


class OnePasswordCSV(CSV):
    """Importer for 1password 6 in CSV format."""
    name = '1password'
    default = False
    version = '6'
    default = False
    url = 'https://1password.com'
    hexport = 'See this guide: https://support.1password.com/export'
    himport = 'pass import 1password file.csv'
    keys = {
        'title': 'Title',
        'password': 'Password',
        'login': 'Username',
        'url': 'URL',
        'comments': 'Notes',
        'group': 'Type'
    }


class OnePassword4CSV(CSV):
    """Importer for 1password 4 in CSV format."""
    name = '1password'
    default = False
    version = '4'
    only = True
    url = 'https://1password.com'
    hexport = 'See this guide: https://support.1password.com/export'
    himport = 'pass import 1password file.csv'
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'notes'
    }


class OnePassword8CSV(CSV):
    """Importer for 1password 8 in CSV format."""
    name = '1password'
    version = '8'
    url = 'https://1password.com'
    hexport = 'See this guide: https://support.1password.com/export'
    himport = 'pass import 1password file.csv'
    keys = {
        'title': 'Title',
        'url': 'Url',
        'login': 'Username',
        'password': 'Password',
        'otpauth': 'OTPAuth',
        'favorite': 'Favorite',
        'archived': 'Archived',
        'tags': 'Tags',
        'comments': 'Notes'
    }


class OnePassword4PIF(JSON):
    """Importer for 1password 4 in PIF format.

    :param list ignore: List of key in the PIF file to not try to import.

    """
    name = '1password'
    format = '1pif'
    default = False
    version = '4'
    url = 'https://1password.com'
    hexport = 'See this guide: https://support.1password.com/export'
    himport = 'pass import 1password file.1pif'
    encoding = 'utf-8-sig'
    ignore = {'keyID', 'typeName', 'uuid', 'openContents', 'URLs'}
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'location',
        'comments': 'notesPlain',
        'group': 'folderUuid',
        'tags': 'tags'
    }

    # Import methods

    @staticmethod
    def pif2json(file):
        """Convert 1pif to json: https://github.com/eblin/1passpwnedcheck."""
        data = file.read()
        cleaned = re.sub(r'(?m)^\*\*\*.*\*\*\*\s+', '', data)
        cleaned = cleaned.split('\n')
        # On 1Password v7.9.11 (macOS), 1PIF export produces 1 extra empty line
        cleaned = [v for v in cleaned if len(v) > 0]
        cleaned = ','.join(cleaned).rstrip(',')
        cleaned = f'[{cleaned}]'
        # JSON string with eventual special characters are encoded properly
        # eg: NUL, TAB
        cleaned = json.dumps(json.loads(cleaned, strict=False))
        return json.loads(cleaned)

    def parse(self):
        """Parse PIF based file."""
        jsons = self.pif2json(self.file)
        keys = self.invkeys()
        folders = {}
        for item in jsons:
            if item.get('typeName', '') == 'system.folder.Regular':
                key = item.get('uuid', '')
                folders[key] = {
                    'group': item.get('title', ''),
                    'parent': item.get('folderUuid', '')
                }

            elif item.get('typeName', '') == 'webforms.WebForm':
                if item.get('trashed', False):
                    continue
                entry = {}
                scontent = item.pop('secureContents', {})
                fields = scontent.pop('fields', [])
                for field in fields:
                    name = field.get('name', '')
                    designation = field.get('designation', '')
                    jsonkey = name or designation
                    key = keys.get(jsonkey, jsonkey)
                    entry[key] = field.get('value', '')

                sections = scontent.get('sections', [])
                for section in sections:
                    for field in section.get('fields', []):
                        value = field.get('v', '')
                        if value.startswith('otpauth://'):
                            entry['otpauth'] = value

                item.update(scontent)
                for key, value in item.items():
                    if key not in self.ignore:
                        entry[keys.get(key, key)] = value

                tags = []
                if 'openContents' in item:
                    open_contents = item['openContents']
                    tags = open_contents.get('tags', [])

                entry['tags'] = tags
                self.data.append(entry)
        self._sortgroup(folders)

    # Format recognition method

    def is_format(self):
        """Return True if the file is a 1PIF file."""
        try:
            self.jsons = self.pif2json(self.file)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            return False
        return True

    def checkheader(self, header, only=False):
        """No header check is needed."""
        return True


register_managers(OnePassword8CSV,
                  OnePasswordCSV, OnePassword4CSV, OnePassword4PIF)
register_detecters(OnePassword4PIF)
