# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.otp import OTP


class AndOTP(OTP):
    """Importer for AndOTP plain or encrypted JSON format."""
    name = 'andotp'
    format = 'json'
    url = 'https://github.com/andOTP/andOTP'
    hexport = 'Backups> Backup plain'
    himport = 'pass import andotp file.json'
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


register_managers(AndOTP)
