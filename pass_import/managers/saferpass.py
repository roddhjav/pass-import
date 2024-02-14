# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class SaferPass(CSV):
    """Importer for SaferPass in CSV format."""
    name = 'saferpass'
    url = 'https://saferpass.net'
    hexport = 'Settings > Export Data: Export data'
    himport = 'pass import saferpass file.csv'
    encoding = 'utf-8-sig'
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'notes',
        'favorite': 'favorite',
        'text': 'text',
        'modelType': 'modelType',
        'color': 'color'
    }


register_managers(SaferPass)
