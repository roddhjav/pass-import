# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Firefox(CSV):
    """Importer for Firefox in CSV format."""
    name = 'firefox'
    url = 'https://www.mozilla.org/en-US/firefox/lockwise/'
    hexport = 'In about:logins Menu: Export logins'
    himport = 'pass import firefox file.csv'
    keys = {'title': 'url', 'password': 'password', 'login': 'username'}

    @classmethod
    def header(cls):
        """Header for Firefox CSV file."""
        return list(cls.keys.values()) + ['httpRealm', 'formActionOrigin',
                                          'timeCreated', 'timeLastUsed',
                                          'timePasswordChanged', 'guid']


class FirefoxPasswordExporter(CSV):
    """Importer for Firefox password exporter extension in CSV format."""
    name = 'firefox'
    default = False
    url = 'https://github.com/kspearrin/ff-password-exporter'
    hexport = 'Add-ons Prefs: Export Passwords: CSV'
    himport = 'pass import firefox file.csv'
    keys = {'title': 'hostname', 'password': 'password', 'login': 'username'}


register_managers(Firefox, FirefoxPasswordExporter)
