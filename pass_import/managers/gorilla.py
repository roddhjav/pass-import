# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import re

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Gorilla(CSV):
    """Importer for Gorilla in CSV format."""
    name = 'gorilla'
    url = 'https://github.com/zdia/gorilla/wiki'
    hexport = 'File > Export: Yes: CSV Files'
    himport = 'pass import gorilla file.csv'
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'user',
        'url': 'url',
        'comments': 'notes',
        'group': 'group'
    }

    def parse(self):
        """Parse Gorilla CSV file."""
        super().parse()
        for entry in self.data:
            group = re.sub(r'(?<=[^\\])\.', os.sep, entry.get('group', ''))
            entry['group'] = re.sub(r'\\.', '.', group)


register_managers(Gorilla)
