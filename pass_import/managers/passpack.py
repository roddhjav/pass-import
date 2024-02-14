# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Passpack(CSV):
    """Importer for Passpack in CSV format."""
    name = 'passpack'
    url = 'https://www.passpack.com'
    hexport = 'Settings > Export > Save to CSV'
    keys = {
        'title': 'Entry Name',
        'password': 'Password',
        'login': 'User ID',
        'url': 'URL',
        'email': 'Email',
        'comments': 'Notes',
        'group': 'Tags'
    }

    def parse(self):
        """Parse Passpack CSV file."""
        super().parse()
        for entry in self.data:
            groups = json.loads(entry.pop('group', '')).get('tags', [])
            for item in groups:
                field = json.loads(item)
                entry['group'] = field.get('tag', '')

            extra = json.loads(entry.pop('Extra Fields',
                                         '')).get('extraFields', [])
            for item in extra:
                field = json.loads(item)
                entry[field.get('name', '')] = field.get('data', '')


register_managers(Passpack)
