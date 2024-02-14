# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class Encryptr(CSV):
    """Importer for Encryptr in CSV format."""
    name = 'encryptr'
    url = 'https://spideroak.com/encryptr'
    hexport = ('Compile from source and follow instructions from this guide: '
               'https://github.com/SpiderOak/Encryptr/issues/295#issuecomment'
               '-322449705')
    himport = 'pass import encryptr file.csv'
    keys = {
        'title': 'Label',
        'password': 'Password',
        'login': 'Username',
        'url': 'Site URL',
        'comments': 'Notes',
        'text': 'Text'
    }

    @classmethod
    def header(cls):
        """Get Encryptr special format header."""
        return ["Entry Type", "Label", "Notes"]


register_managers(Encryptr)
