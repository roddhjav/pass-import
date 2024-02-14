# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.managers import PasswordStore


class Gopass(PasswordStore):
    """Importer & Exporter for gopass."""
    name = 'gopass'
    format = 'gopass'
    command = 'gopass'
    url = 'https://www.gopass.pw/'
    himport = 'pass import gopass path/to/store'


register_managers(Gopass)
