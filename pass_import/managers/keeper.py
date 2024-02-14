# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class KeeperCSV(CSV):
    """Importer for Keeper in CSV format."""
    name = 'keeper'
    url = 'https://keepersecurity.com'
    hexport = 'Settings > Export : Export to CSV File'
    himport = 'pass import keeper file.csv'
    fieldnames = ['group', 'title', 'login', 'password', 'url', 'comments']
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'login',
        'url': 'url',
        'comments': 'comments',
        'group': 'group'
    }


register_managers(KeeperCSV)
