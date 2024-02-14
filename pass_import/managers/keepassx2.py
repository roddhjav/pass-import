# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV
from pass_import.formats.kdbx import KDBX


class Keepassx2CSV(CSV):
    """Importer for KeepassX2 in CSV format."""
    name = 'keepassx2'
    default = False
    url = 'https://www.keepassx.org'
    hexport = 'Database > Export to CSV File'
    himport = 'pass import keepassx2 file.csv'
    keys = {
        'title': 'Title',
        'password': 'Password',
        'login': 'Username',
        'url': 'URL',
        'comments': 'Notes',
        'group': 'Group'
    }


class Keepassx2KDBX(KDBX):
    """Importer for KeepassX2 encrypted KDBX format."""
    name = 'keepassx2'
    url = 'https://www.keepassx.org'
    himport = 'pass import keepassx2 file.kdbx'


register_managers(Keepassx2CSV, Keepassx2KDBX)
