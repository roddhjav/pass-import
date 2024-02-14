# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class PadlockCSV(CSV):
    """Importer for Padloc CSV format."""
    name = 'padlock'
    url = 'https://padloc.app'
    hexport = 'Settings > Export Data and copy text into a .csv file'
    himport = 'pass import padlock file.csv'
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'notes',
        'group': 'tags'
    }

    def parse(self):
        """Parse Padloc CSV file."""
        super().parse()
        for entry in self.data:
            entry['group'] = entry.get('group', '').replace('\\', os.sep)


register_managers(PadlockCSV)
