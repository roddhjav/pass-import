# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json

from pass_import.formats.json import JSON


class OTP(JSON):
    """Base class for OTP based importers."""
    content = ''

    # Import methods

    @staticmethod
    def _otp(item):
        otp = f"otpauth://{item.get('type', 'totp').lower()}/totp-secret?"
        otp += f"secret={item['secret']}&issuer={item['label']}"
        for setting in ['algorithm', 'digits', 'counter', 'period']:
            if setting in item:
                otp += f"&{setting}={item[setting]}"
        return otp

    def parse(self):
        """Parse OTP based file."""
        jsons = json.loads(self.content)
        for item in jsons:
            entry = {}
            entry['title'] = item['label']
            entry['otpauth'] = self._otp(item)

            for key in ['type', 'thumbnail', 'last_used']:
                entry[key] = str(item.get(key, '')).lower()
            entry['tags'] = ', '.join(item['tags'])
            self.data.append(entry)

    # Context manager method

    def open(self):
        """Parse OTP based file."""
        super().open()
        self.content = self.file.read()
