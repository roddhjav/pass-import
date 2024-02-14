# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.yaml import YAML


class Passpie(YAML):
    """Importer for Passpie in YAML format."""
    name = 'passpie'
    version = '1.0'
    url = 'https://www.enpass.io'
    hexport = '`passpie export file.yml`'
    himport = 'pass import passpie file.yml'
    yml_format = {'handler': 'passpie', 'version': 1.0}
    rootkey = 'credentials'
    keys = {
        'title': 'name',
        'password': 'password',
        'login': 'login',
        'comments': 'comment'
    }


register_managers(Passpie)
