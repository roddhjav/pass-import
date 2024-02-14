# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import csv
import json

from pass_import.core import register_managers
from pass_import.errors import FormatError
from pass_import.formats.csv import CSV
from pass_import.formats.json import JSON


class Enpass(CSV):
    """Importer for Enpass in CSV format."""
    name = 'enpass'
    default = False
    url = 'https://www.enpass.io'
    hexport = 'File > Export > As CSV'
    himport = 'pass import enpass file.csv'
    csv_header = '"Title","Field","Value","Field","Value",.........,"Note"'
    keys = {
        'title': 'Title',
        'password': 'Password',
        'login': 'Username',
        'url': 'URL',
        'comments': 'notes',
        'group': 'group'
    }

    def parse(self):
        """Parse Enpass CSV file."""
        if not self.file.readline().startswith(self.csv_header):
            raise FormatError()
        reader = csv.reader(self.file)
        keys = self.invkeys()
        for row in reader:
            entry = {}
            entry['title'] = row.pop(0)
            entry['comments'] = row.pop()
            index = 0
            while index + 2 <= len(row):
                key = keys.get(row[index], row[index])
                entry[key] = row[index + 1]
                index += 2

            self.data.append(entry)

    @classmethod
    def header(cls):
        """Header for Enpass CSV file."""
        return cls.csv_header.replace('"', '').split(',')


class Enpass6(JSON):
    """Importer for Enpass 6 in JSON format."""
    name = 'enpass'
    version = '6'
    url = 'https://www.enpass.io'
    hexport = 'Menu > File > Export > As JSON'
    himport = 'pass import enpass file.json'
    ignore = {'fields', 'folders', 'icon'}
    keyslist = [
        'title', 'password', 'login', 'url', 'comments', 'group', 'email'
    ]
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'website',
        'comments': 'note',
        'group': 'group',
        'email': 'e-mail'
    }
    json_header = {
        'folders': [{
            'icon': str,
            'parent_uuid': str,
            'title': str,
            'updated_at': int,
            'uuid': str
        }],
        'items': [{
            'auto_submit': int,
            'category': str,
            'favorite': int,
            'fields': [{
                'label': str,
                'type': str,
                'value': str
            }],
            'folders': list,
            'icon': dict,
            'note': str,
            'subtitle': str,
            'template_type': str,
            'title': str,
            'uuid': str
        }],
    }

    def parse(self):
        """Parse Enpass 6 JSON file."""
        jsons = json.loads(self.file.read())
        keys = self.invkeys()
        folders = {}
        for item in jsons.get('folders', {}):
            key = item.get('uuid', '')
            folders[key] = {
                'group': item.get('title', ''),
                'parent': item.get('parent_uuid', '')
            }

        for item in jsons.get('items', {}):
            entry = {}
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


register_managers(Enpass, Enpass6)
