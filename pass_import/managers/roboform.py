# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Roboform(CSV):
    """Importer for Roboform in CSV format."""
    name = 'roboform'
    url = 'https://www.roboform.com'
    hexport = 'Roboform > Options > Data & Sync > Export To: CSV file'
    himport = 'pass import roboform file.csv'
    keys = {
        'title': 'Name',
        'password': 'Pwd',
        'login': 'Login',
        'url': 'Url',
        'comments': 'Note',
        'group': 'Folder'
    }


register_managers(Roboform)
