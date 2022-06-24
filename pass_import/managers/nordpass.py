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


register_managers(NordPassCSV)
