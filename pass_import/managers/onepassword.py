# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV
from pass_import.formats.json import PIF


class OnePasswordCSV(CSV):
    """Importer for 1password 6 in CSV format."""
    name = '1password'
    version = '6'
    url = 'https://1password.com'
    hexport = 'See this guide: https://support.1password.com/export'
    himport = 'pass import 1password file.csv'
    keys = {
        'title': 'Title',
        'password': 'Password',
        'login': 'Username',
        'url': 'URL',
        'comments': 'Notes',
        'group': 'Type'
    }


class OnePassword4CSV(CSV):
    """Importer for 1password 4 in CSV format."""
    name = '1password'
    default = False
    version = '4'
    only = True
    url = 'https://1password.com'
    hexport = 'See this guide: https://support.1password.com/export'
    himport = 'pass import 1password file.csv'
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'notes'
    }


class OnePassword4PIF(PIF):
    """Importer for 1password 4 in PIF format."""
    name = '1password'
    default = False
    version = '4'
    url = 'https://1password.com'
    hexport = 'See this guide: https://support.1password.com/export'
    himport = 'pass import 1password file.1pif'
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'location',
        'comments': 'notesPlain',
        'group': 'folderUuid'
    }


register_managers(OnePasswordCSV, OnePassword4CSV, OnePassword4PIF)
