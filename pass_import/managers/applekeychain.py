# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
# Copyright (C) 2019 Santi González https://github.com/santigz
#

import re
from datetime import datetime

try:
    from defusedxml import ElementTree
except ImportError:
    from xml.etree import ElementTree

import yaml
from pass_import.core import Cap, register_detecters, register_managers
from pass_import.detecter import Formatter
from pass_import.manager import PasswordImporter


class AppleKeychain(Formatter, PasswordImporter):
    """Importer for Apple Keychain."""
    cap = Cap.FORMAT | Cap.IMPORT
    name = 'apple-keychain'
    format = 'keychain'
    url = 'https://support.apple.com/guide/keychain-access'
    hexport = ('See this guide: https://gist.github.com/santigz/'
               '601f4fd2f039d6ceb2198e2f9f4f01e0')
    himport = 'pass import applekeychain file.txt'
    keychain_format = ['version', 'class', 'data', 'attributes']
    keys = {
        'title': 7,
        'login': 'acct',
        'authentication_type': 'atyp',
        'creation_date': 'cdat',
        'creator': 'crtr',
        'description': 'desc',
        'alt_comment': 'crtr',
        'modification_date': 'mdat',
        'password_path': 'path',
        'protocol': 'ptcl',
        'url': 'srvr',
        'security_domain': 'sdmn',
        'service': 'svce'
    }
    yamls = None

    # Import methods

    @staticmethod
    def keychain2yaml(file):
        """Convert keychain to yaml."""
        yamls = []
        data = file.read()
        characters = {
            'data:\n': 'data: ',
            '<NULL>': '',
            r'<[\w]*>=': ': ',
            '0x00000007 :': '0x00000007:',
            '0x00000008 :': '0x00000008:',
            'keychain: "([^"]*)"': '---'
        }
        for key, value in characters.items():
            data = re.sub(key, value, data)
        data = data.strip('---').split('---')
        for block in data:
            yamls.append(yaml.safe_load(block))
        return yamls

    @staticmethod
    def _compose_url(entry):
        """Compose the URL from Apple non-standard protocol names."""
        sub = {
            'htps': 'https',
            'ldps': 'ldaps',
            'ntps': 'nntps',
            'sox': 'socks',
            'teln': 'telnet',
            'tels': 'telnets',
            'imps': 'imaps',
            'pops': 'pop3s'
        }
        url = entry.get('url', '')
        protocol = entry.get('protocol', '')
        if url and protocol:
            url = f"{sub.get(protocol, protocol)}://{url.strip()}"
        return url

    @staticmethod
    def _human_date(date):
        """Return the date in human readable format."""
        try:
            if date[-1:] == '\x00':
                date = date[:-1]
            thedate = datetime.strptime(date, '%Y%m%d%H%M%SZ')
            return str(thedate)
        except (ValueError, UnicodeError):  # pragma: no cover
            return date

    @staticmethod
    def _decode(string):
        """Extract and decode hexadecimal value from a string."""
        hexmod = re.findall(r'0x[0-9A-F]*', string)
        if hexmod:
            return bytes.fromhex(hexmod[0][2:]).decode('utf-8')
        return string

    def _decode_data(self, entry):
        """Decode data field (password or comments)."""
        key = entry.get('type', 'password')
        key = 'comments' if key == 'note' else key
        data = entry.pop('data', '')
        if isinstance(data, int):
            return key, ''

        data = self._decode(data)
        if key == 'comments':
            if data:
                try:
                    tree = ElementTree.XML(data)
                except ElementTree.ParseError:
                    return key, ''

                found = tree.find('.//string')
                if found is None:
                    return key, ''
                return key, found.text
            return key, ''
        return key, data

    def parse(self):
        """Parse apple-keychain format by converting it in yaml first."""
        yamls = self.keychain2yaml(self.file)
        keys = self.invkeys()
        for block in yamls:
            entry = {}
            attributes = block.pop('attributes', {})
            block.update(attributes)
            for key, value in block.items():
                if value is not None:
                    entry[keys.get(key, key)] = value

            key, value = self._decode_data(entry)
            entry[key] = value
            entry['url'] = self._compose_url(entry)
            for key in ['creation_date', 'modification_date']:
                entry[key] = self._human_date(self._decode(entry.get(key, '')))

            self.data.append(entry)

    # Format recognition methods

    def is_format(self):
        """Check keychain file format."""
        try:
            self.yamls = self.keychain2yaml(self.file)
            if isinstance(self.yamls, str):
                return False
        except (yaml.scanner.ScannerError, yaml.parser.ParserError,
                UnicodeDecodeError):
            return False
        return True

    def checkheader(self, header, only=False):
        """Check keychain format."""
        if isinstance(self.yamls, list):
            self.yamls = self.yamls[0]
        for yamlkey in header:
            if yamlkey not in self.yamls:
                return False
        return True

    @classmethod
    def header(cls):
        """Get keychain format header."""
        return cls.keychain_format


register_managers(AppleKeychain)
register_detecters(AppleKeychain)
