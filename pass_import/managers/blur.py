# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json

from pass_import.core import register_managers
from pass_import.formats.csv import CSV
from pass_import.formats.json import JSON


class BlurCSV(CSV):
    """Importer for Blur in CSV format."""
    name = 'blur'
    secure = False
    default = False
    url = 'https://abine.com'
    hexport = 'Settings: Export Data: Export CSV: Accounts: Export CSV'
    himport = 'pass import blur file.csv'
    keys = {
        'title': 'label',
        'password': 'password',
        'login': 'username',
        'email': 'email',
        'url': 'domain',
    }

    def parse(self):
        """Parse Blur CSV file."""
        super().parse()
        for entry in self.data:
            for key in entry:
                if entry[key] == 'undefined':
                    entry[key] = ''


class BlurJSON(JSON):
    """Importer for Blur in JSON format."""
    name = 'blur'
    secure = False
    url = 'https://abine.com'
    hexport = 'Settings: Export Data: Export Blur Data'
    himport = 'pass import blur file.json'
    ignore = {'id'}
    keys = {
        'title': 'label',
        'password': 'password',
        'login': 'username',
        'email': 'email',
        'url': 'domain',
        'comments': 'description'
    }
    json_header = {
        'dntmeExport': True,
        'accounts': list,
        'cards': list,
        'addresses': list,
        'notes': list,
        'identities': list,
    }

    def parse(self):
        """Parse Blur JSON file."""
        jsons = json.loads(self.file.read())
        keys = self.invkeys()

        items = []
        for key in ['accounts', 'cards', 'addresses', 'notes', 'identities']:
            items.extend(jsons.get(key, []))

        for item in items:
            entry = {}
            for key, value in item.items():
                if key in self.ignore or value == 'undefined':
                    continue
                entry[keys.get(key, key)] = value
            self.data.append(entry)


register_managers(BlurCSV, BlurJSON)
