# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2022 Shashwat Pragya <shashwat183@gmail.com>.
#

from pass_import.formats.csv import CSV
from pass_import.core import register_managers


class NordPassCSV(CSV):
    """Importer for Nord Pass in CSV format."""
    name = 'nordpass'
    url = 'https://nordpass.com/'
    hexport = 'Settings > Export Items'
    himport = 'pass import nordpass file.csv'
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'note',
        'group': 'folder'
    }

    def parse(self):
        """Parse NordPass CSV file."""
        super().parse()
        # NordPass exports individual folders as their own
        # empty rows. This code removes the extra folder entries
        # from the parsed data.
        groups = []
        for entry in self.data:
            if entry['group']:
                groups.append(entry['group'])

        self.data = list(filter(
            lambda x: not (x['title'] in groups and not x['group']),
            self.data))


register_managers(NordPassCSV)
