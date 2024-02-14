# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json

from pass_import.core import register_managers
from pass_import.formats.csv import CSV
from pass_import.formats.json import JSON


class DashlaneCSV(CSV):
    """Importer for Dashlane in CSV format."""
    name = 'dashlane'
    url = 'https://www.dashlane.com'
    hexport = 'File > Export > Unsecured Archive in CSV'
    himport = 'pass import dashlane file.csv'
    fieldnames = ['title', 'url', 'login', 'password', 'comments']
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'login',
        'url': 'url',
        'comments': 'comments'
    }


class DashlaneJSON(JSON):
    """Importer for Dashlane in JSON format."""
    name = 'dashlane'
    default = False
    url = 'https://www.dashlane.com'
    hexport = 'File > Export > Unsecured Archive in JSON'
    himport = 'pass import dashlane file.json'
    keys = {
        'title': 'title',
        'password': 'password',
        'email': 'email',
        'login': 'login',
        'url': 'domain',
        'comments': 'note',
    }
    json_header = {
        'AUTHENTIFIANT': list,
        'EMAIL': list
    }

    def parse(self):
        """Parse Dashlane JSON file."""
        jsons = json.loads(self.file.read())
        keys = self.invkeys()
        for item in jsons.get('AUTHENTIFIANT', {}):
            entry = {}
            for key, value in item.items():
                entry[keys.get(key, key)] = value

            self.data.append(entry)


register_managers(DashlaneCSV, DashlaneJSON)
