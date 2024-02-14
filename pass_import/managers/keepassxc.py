# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.kdbx import KDBX
from pass_import.managers.keepassx2 import Keepassx2CSV


class KeepassxcCSV(Keepassx2CSV):
    """Importer for KeepassXC in CSV format."""
    name = 'keepassxc'
    default = False
    url = 'https://keepassxc.org'
    hexport = 'Database > Export to CSV File'
    himport = 'pass import keepassxc file.csv'


class KeepassxcKDBX(KDBX):
    """Importer for KeepassXC encrypted KDBX format."""
    name = 'keepassxc'
    url = 'https://keepassxc.org'
    himport = 'pass import keepassxc file.kdbx'


register_managers(KeepassxcCSV, KeepassxcKDBX)
