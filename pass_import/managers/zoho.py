# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class ZohoCSV(CSV):
    """Importer for Zoho in CSV format."""
    name = 'zoho'
    url = 'https://www.zoho.com/vault'
    hexport = 'Tools > Export Secrets: Zoho Vault Format CSV'
    himport = 'pass import zoho file.csv'
    only = True
    encoding = 'utf-8-sig'
    keys = {
        'title': 'Secret Name',
        'url': 'Secret URL',
        'comments': 'Notes'
    }

    def parse(self):
        """Parse Zoho CSV file."""
        super().parse()
        for entry in self.data:
            secret = entry.pop(None, ['', ''])
            entry['login'] = secret[0]
            entry['password'] = secret[1]


class ZohoCSVVault(CSV):
    """Importer for Zoho Vault in CSV format."""
    name = 'zoho'
    default = False
    url = 'https://www.zoho.com/vault'
    hexport = 'Tools > Export Secrets: Zoho Vault Format CSV'
    himport = 'pass import zoho file.csv'
    encoding = 'utf-8-sig'
    keys = {
        'title': 'Secret Name',
        'description': 'Description',
        'url': 'Secret URL',
        'comments': 'Notes',
        'group': 'ChamberName',
        'tags': 'Tags',
        '_data': 'SecretData',
        '_custom': 'CustomData',
    }

    def parse(self):
        """Parse Zoho CSV Vault file."""
        super().parse()
        keys = {
            'SecretType': 'type',
            'Password': 'password',
            'User Name': 'login'
        }
        for entry in self.data:
            entry.pop(None, None)
            entry['group'] = entry.get('group', '').replace('\n', os.sep)

            items = []
            items.extend(entry.pop('_data', '\n').split('\n'))
            items.extend(entry.pop('_custom', '\n').split('\n'))
            for item in items:
                if ':' in item:
                    key, value = item.split(':', 1)
                    entry[keys.get(key, key)] = value


register_managers(ZohoCSV, ZohoCSVVault)
