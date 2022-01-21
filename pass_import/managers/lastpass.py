# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.errors import FormatError
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
        super().parse()
        for entry in self.data:
            if 'group' in entry and entry['group'] is None:
                # LastPass will truncate everything after `$` in a
                # secure note entry when exporting as a CSV, including
                # any closing ", leaving the file in a corrupt
                # state. Triggering this is likely a symptom of such a
                # corrupted export.
                #
                # Likewise, it also has problems exporting single
                # quotes in the password field, causing all data prior
                # to the single quote (including the url field, etc.)
                # to be truncated, leading to the parser thinking the
                # path field wasn't included, and incorrectly
                # resulting in a value of None.
                raise FormatError(f'Invalid group in entry:\n{entry}.')
            entry['group'] = entry.get('group', '').replace('\\', os.sep)


register_managers(LastpassCSV)
