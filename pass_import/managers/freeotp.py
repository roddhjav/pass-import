# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import base64
import json

from pass_import.core import register_managers
from pass_import.formats.otp import OTP


class FreeOTPPlus(OTP):
    """Importer for FreeOTPPlus in JSON format."""
    name = 'freeotp+'
    format = 'json'
    url = 'https://github.com/helloworld1/FreeOTPPlus'
    hexport = 'Settings> Export> Export JSON Format'
    himport = 'pass import freeotp+ file.json'
    json_header = {
        'tokenOrder': list,
        'tokens': [{
            'algo': str,
            'digits': int,
            'issuerExt': str,
            'label': str,
            'secret': list,
            'type': str
        }]
    }

    def parse(self):
        """Parse FreeOTP+ JSON file."""
        jsons = json.loads(self.content)
        for item in jsons['tokens']:
            item['label'] = item['issuerExt']
            item['algorithm'] = item['algo']
            item['secret'] = base64.b32encode(
                bytes(x & 0xff for x in item['secret'])).decode("utf8")

            entry = {}
            entry['title'] = item['issuerExt']
            entry['otpauth'] = self._otp(item)
            entry['type'] = item['type'].lower()
            self.data.append(entry)


register_managers(FreeOTPPlus)
