# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2022 Artyom Yurash <urashav@ya.ru>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class SafeInCloudCSV(CSV):
    """Importer for SafeInCloud in CSV format."""
    name = 'safeincloud'
    url = 'https://safeincloud.ladesk.com/'
    hexport = 'File > Export > Comma-Separated Values (CSV)'
    himport = 'pass import safeincloud file.csv'
    keys = {
        'title': 'Title',
        'login': 'Login',
        'password': 'Password',
        'url': 'URL',
        'comments': 'Notes',
        'otpauth': 'OTP'
    }


register_managers(SafeInCloudCSV)
