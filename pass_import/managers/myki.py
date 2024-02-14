# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Myki(CSV):
    """Importer for Myki in CSV format."""
    name = 'myki'
    url = 'https://myki.com'
    hexport = ('See this guide: https://support.myki.com/myki-app/export'
               'ing-your-passwords-from-the-myki-app/how-to-export-your'
               '-passwords-account-data-from-myki')
    himport = 'pass import myki file.csv'
    keys = {
        'title': 'nickname',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'additionalInfo',
        'otpauth': 'twofaSecret',
    }


register_managers(Myki)
