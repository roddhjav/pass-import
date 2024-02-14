# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.otp import OTP


class GnomeAuthenticator(OTP):
    """Importer for Gnome Authenticator in JSON format."""
    name = 'gnome-auth'
    url = 'https://gitlab.gnome.org/World/Authenticator'
    hexport = 'Backup > in a plain-text JSON file'
    himport = 'pass import gnome-authenticator file.json'
    json_header = [{
        'secret': str,
        'label': str,
        'digits': int,
        'type': str,
        'algorithm': str,
        'thumbnail': str,
        'last_used': int,
        'tags': list
    }]


register_managers(GnomeAuthenticator)
