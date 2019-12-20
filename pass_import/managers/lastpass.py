# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class LastpassCSV(CSV):
    """Importer for Lastpass in CSV format."""
    name = 'lastpass'
    url = 'https://www.lastpass.com'
    hexport = 'More Options > Advanced > Export'
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'extra',
        'group': 'grouping'
    }

    def parse(self):
        """Parse Lastpass CSV file."""
        super(LastpassCSV, self).parse()
        for entry in self.data:
            entry['group'] = entry.get('group', '').replace('\\', os.sep)


register_managers(LastpassCSV)
