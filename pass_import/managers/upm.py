# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class UPM(CSV):
    """Importer for Universal Password Manager (UPM) in CSV format."""
    name = 'upm'
    url = 'http://upm.sourceforge.net'
    hexport = 'Database > Export'
    himport = 'pass import upm file.csv'
    fieldnames = ['title', 'login', 'password', 'url', 'comments']
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'login',
        'url': 'url',
        'comments': 'comments'
    }


register_managers(UPM)
