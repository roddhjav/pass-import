# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Buttercup(CSV):
    """Importer for Buttercup in CSV format."""
    name = 'buttercup'
    url = 'https://buttercup.pw'
    hexport = 'File > Export > Export File to CSV'
    himport = 'pass import buttercup file.csv'
    ignore = {'!group_id', 'id'}
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'URL',
        'comments': 'Notes',
        'group': '!group_name'
    }

    def parse(self):
        """Parse Buttercup CSV file."""
        super(Buttercup, self).parse()
        for entry in self.data:
            for key in self.ignore:
                entry.pop(key, None)


register_managers(Buttercup)
