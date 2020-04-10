# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class ChromeCSV(CSV):
    """Importer for Chrome in CSV format."""
    name = 'chrome'
    url = 'https://support.google.com/chrome'
    hexport = ('See this guide: https://www.axllent.org/docs/view/'
               'export-chrome-passwords')
    himport = 'pass import chrome file.csv'
    only = True
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'username',
        'url': 'url'
    }


class ChromeCSVSQLite(CSV):
    """Importer for Chrome SQLite in CSV format."""
    name = 'chrome'
    default = False
    url = 'https://support.google.com/chrome'
    hexport = ('See this guide: https://www.axllent.org/docs/view/'
               'export-chrome-passwords')
    himport = 'pass import chrome file.csv'
    keys = {
        'title': 'display_name',
        'password': 'password_value',
        'login': 'username_value',
        'url': 'origin_url'
    }


register_managers(ChromeCSV, ChromeCSVSQLite)
