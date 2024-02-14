# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Buttercup(CSV):
    """Importer for Buttercup in CSV format."""
    name = 'buttercup'
    url = 'https://buttercup.pw'
    hexport = 'File > Export > Export File to CSV'
    himport = 'pass import buttercup file.csv'
    ignore = {'!type', '!group_name', '!group_parent', 'id'}
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'URL',
        'comments': 'Notes',
        'group': '!group_id'
    }

    def parse(self):
        """Parse Buttercup CSV file."""
        super().parse()

        # Get group structure
        folders = {}
        groups = []
        for entry in self.data:
            if entry.get('!type', '') == 'group':
                key = entry.get('group', '0')
                folders[key] = {
                    'group': entry.get('!group_name', ''),
                    'parent': entry.get('!group_parent', '0')
                }
                groups.append(entry)
        self._sortgroup(folders)

        # Remove groups declaration from ``data``
        for entry in groups:
            self.data.remove(entry)

        # Remove ignored key from entries
        for entry in self.data:
            for key in self.ignore:
                entry.pop(key, None)


register_managers(Buttercup)
