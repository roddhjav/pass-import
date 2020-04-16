# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class FirefoxPasswordExporter(CSV):
    """Importer for Firefox password exporter extension in CSV format."""
    name = 'firefox'
    url = 'https://github.com/kspearrin/ff-password-exporter'
    hexport = 'Add-ons Prefs: Export Passwords: CSV'
    himport = 'pass import firefox file.csv'
    keys = {'title': 'hostname', 'password': 'password', 'login': 'username'}


register_managers(FirefoxPasswordExporter)
