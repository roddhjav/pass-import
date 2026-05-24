# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2024 SAY-5 <say.apm35@gmail.com>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class SynologyC2CSV(CSV):
    """Importer for Synology C2 Password in CSV format."""
    name = 'synology'
    url = 'https://c2.synology.com/en-global/password/overview'
    hexport = 'Profile > Export > Download'
    himport = 'pass import synology file.csv'
    encoding = 'utf-8-sig'
    keys = {
        'title': 'Display_Name',
        'login': 'Login_Username',
        'password': 'Login_Password',
        'url': 'Login_URLs',
        'otpauth': 'Login_TOTP',
        'comments': 'Notes'
    }


register_managers(SynologyC2CSV)
