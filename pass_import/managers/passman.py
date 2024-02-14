# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json
import os

from pass_import.clean import replaces
from pass_import.core import register_managers
from pass_import.formats.csv import CSV
from pass_import.formats.json import JSON


class PassmanCSV(CSV):
    """Importer for Passman in CSV format."""
    name = 'passman'
    url = 'https://passman.cc'
    hexport = 'Settings > Export credentials  > Export type: CSV'
    himport = 'pass import passman file.csv'
    keys = {
        'title': 'label',
        'password': 'password',
        'login': 'username',
        'email': 'email',
        'url': 'url',
        'comments': 'description',
        'group': 'tags'
    }

    def parse(self):
        """Parse Passman CSV file."""
        super().parse()
        characters = {'\\': os.sep, '[': '', ']': ''}
        for entry in self.data:
            entry['group'] = replaces(characters, entry.get('group', ''))


class PassmanJSON(JSON):
    """Importer for Passman in JSON format."""
    name = 'passman'
    default = False
    url = 'https://passman.cc'
    hexport = 'Settings > Export credentials  > Export type: JSON'
    himport = 'pass import passman file.json'
    keys = {
        'title': 'label',
        'login': 'username',
        'comments': 'description',
        'otpauth': 'otp'
    }
    json_header = [{
        'credential_id': int,
        'guid': str,
        'user_id': str,
        'label': str,
        'description': str,
        'tags': list,
        'username': str,
        'password': str,
        'url': str,
        'icon': dict,
        'custom_fields': list,
        'otp': dict,
        'compromised': bool
    }]

    def parse(self):
        """Parse Passman JSON file."""
        ignore = {'custom_fields', 'icon', 'tags'}
        keys = self.invkeys()
        jsons = json.loads(self.file.read())
        for item in jsons:
            entry = {}
            if item['tags']:
                group = item['tags'][0]['text']
                entry['group'] = group.replace('\\', os.sep)
            custom_fields = item.get('custom_fields', [])
            for field in custom_fields:
                item.update({field['label']: field['value']})

            for key, value in item.items():
                if key not in ignore:
                    entry[keys.get(key, key)] = value

            self.data.append(entry)


register_managers(PassmanCSV, PassmanJSON)
