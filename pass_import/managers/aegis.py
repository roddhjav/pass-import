# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import base64
import json

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    CRYPTOGRAPHY = True
except ImportError:
    CRYPTOGRAPHY = False

from pass_import.core import register_managers
from pass_import.errors import FormatError
from pass_import.formats.otp import OTP
from pass_import.tools import getpassword


class Aegis(OTP):
    """Importer for Aegis otp plain JSON format."""
    name = 'aegis'
    format = 'json'
    url = 'https://github.com/beemdevelopment/Aegis'
    hexport = 'Settings> Tools: Export Plain'
    himport = 'pass import aegis file.json'
    json_header = {
        'version': 1,
        'header': {
            'slots': None,
            'params': None,
        },
        'db': {
            'version': 1,
            'entries': [{
                'type': str,
                'uuid': str,
                'name': str,
                'issuer': str,
                'info': {
                    'secret': str,
                    'algo': str,
                    'digits': int
                }
            }]
        }
    }

    def parse(self):
        """Parse Aegis plain JSON file."""
        self.content = json.loads(self.content)
        if 'db' in self.content:
            self.content = self.content['db']

        for item in self.content.get('entries', []):
            entry = {}
            info = item.pop('info', {})
            item.update(info)
            item['algorithm'] = item.pop('algo', None)
            entry['title'] = item['issuer'] + item['name']
            item['label'] = entry['title']
            entry['otpauth'] = self._otp(item)

            for key in ['group', 'type', 'icon']:
                entry[key] = str(item.get(key, '')).lower()
            self.data.append(entry)


class AegisCipher(Aegis):
    """Importer for Aegis otp encrypted JSON format."""
    name = 'aegis'
    format = 'json'
    default = False
    url = 'https://github.com/beemdevelopment/Aegis'
    hexport = 'Settings> Tools: Export encrypted'
    himport = 'pass import aegis file.json'
    json_header = {
        'version': 1,
        'header': {
            'slots': [{
                'type': int,
                'uuid': str,
                'key': str,
                'key_params': dict
            }],
            'params': {
                'nonce': str,
                'tag': str
            },
        },
        'db': str,
    }

    def decrypt(self, jsons):
        """Import file is AES GCM encrypted, let's decrypt it.

        Based on the import script from Aegis:
        https://github.com/beemdevelopment/Aegis/blob/master/scripts/decrypt.py
        Format documentation:
        https://github.com/beemdevelopment/Aegis/blob/master/docs/vault.md
        """
        if not CRYPTOGRAPHY:
            raise ImportError(name='cryptography')

        password = getpassword(self.prefix)
        master_key = None
        for slot in jsons['header']['slots']:
            if slot['type'] != 1:
                continue

            kdf = Scrypt(salt=bytes.fromhex(slot['salt']),
                         length=32,
                         n=slot['n'],
                         r=slot['r'],
                         p=slot['p'],
                         backend=default_backend())
            key = kdf.derive(password.encode("utf-8"))

            cipher = AESGCM(key)
            param = slot['key_params']
            try:
                nonce = bytes.fromhex(param['nonce'])
                data = bytes.fromhex(slot['key']) + bytes.fromhex(param['tag'])
                master_key = cipher.decrypt(nonce=nonce,
                                            data=data,
                                            associated_data=None)
            except InvalidTag:  # pragma: no cover
                pass

        if master_key is None:  # pragma: no cover
            raise FormatError("unable to decrypt the master key.")

        cipher = AESGCM(master_key)
        param = jsons['header']['params']
        content = base64.b64decode(jsons['db']) + bytes.fromhex(param['tag'])
        plain = cipher.decrypt(nonce=bytes.fromhex(param['nonce']),
                               data=content,
                               associated_data=None)
        return plain.decode('utf-8')

    def parse(self):
        """Parse Aegis encrypted JSON file."""
        self.content = self.decrypt(json.loads(self.content))
        super().parse()


register_managers(Aegis, AegisCipher)
