# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import re
import uuid

try:
    from pykeepass import PyKeePass
    from pykeepass.exceptions import (CredentialsError, HeaderChecksumError,
                                      PayloadChecksumError)
    PYKEEPASS = True
except ImportError:
    PYKEEPASS = False

from pass_import.core import Cap, register_detecters
from pass_import.detecter import Formatter
from pass_import.errors import PMError
from pass_import.manager import PasswordExporter, PasswordImporter
from pass_import.tools import getpassword


class KDBX(Formatter, PasswordImporter, PasswordExporter):
    """Base class for KDBX based importer & exporter.

    The importer supports binary attachments. It requires PyKeePass to run.

    :param PyKeePass keepass: The keepass repository to work on.
    :param list attributes: List of the attributes of PyKeePass to import.

    """
    cap = Cap.FORMAT | Cap.IMPORT | Cap.EXPORT
    name = 'keepass'
    format = 'kdbx'
    magic = b'\x03\xd9\xa2\x9a'
    keys = {'login': 'username', 'comments': 'notes', 'group': 'path'}
    attributes = {
        'title', 'username', 'password', 'url', 'notes', 'icon', 'tags',
        'autotype_enabled', 'autotype_sequence', 'is_a_history_entry'
    }
    reference = re.compile(r'\{REF:([A-Z])@I:([0-9A-F]{32})\}')

    def __init__(self, prefix=None, settings=None):
        self.keepass = None
        settings = {} if settings is None else settings
        keyfile = settings.get('key', '')
        self.keyfile = None if keyfile == '' else keyfile
        super().__init__(prefix, settings)

    # Import methods

    def _getentry(self, kpentry):
        entry = {}
        if kpentry.path is not None:
            entry['group'] = ''
            for item in kpentry.path:
                if item is not None:
                    entry['group'] = os.path.join(entry['group'], item)
        keys = self.invkeys()
        for attr in self.attributes:
            if hasattr(kpentry, attr):
                value = getattr(kpentry, attr)
                if isinstance(value, str):
                    value = self._subref(value)
                entry[keys.get(attr, attr)] = value
        for key, value in kpentry.custom_properties.items():
            if isinstance(value, str):
                value = self._subref(value)
            entry[key] = value
        if kpentry.otp is not None:
            otpauth = kpentry.otp
        else:
            otpauth = self._getotpauth(kpentry.custom_properties)
        if otpauth:
            entry['otpauth'] = otpauth
        return entry

    @staticmethod
    def _getotpauth(properties):
        # KeeWeb style
        if 'otp' in properties:
            return properties['otp']

        issuer = 'Imported'
        # KeePass 2.47 {TIMEOTP} style
        if 'TimeOtp-Secret-Base32' in properties:
            seed = properties['TimeOtp-Secret-Base32']
            digits = '6'

        # KeeTrayTOTP style
        elif 'TOTP Seed' in properties:
            seed = properties['TOTP Seed']
            # Special-case Steam
            if 'TOTP Settings' in properties \
                    and properties['TOTP Settings'] == '30;S':
                digits = 's'      # Android Password Store needs digits==s
                issuer = 'Steam'  # pass-otp, via Pass::Otp, needs issuer=Steam
            else:
                # TODO: parse non-'30;6' settings
                digits = '6'
        else:
            return None

        # Many sites print the secret with spaces
        seed = seed.replace(' ', '')

        return ('otpauth://totp/totp-secret?'
                f'secret={seed}&issuer={issuer}&digits={digits}&period=30')

    def _subref(self, value):
        while True:
            match = self.reference.search(value)
            if match is None:
                break
            cat, attid = match.group(1, 2)
            if cat not in ('U', 'P'):
                break
            start, end = match.start(0), match.end(0)
            kpentry = self.keepass.find_entries(
                uuid=uuid.UUID(attid), first=True)
            if kpentry is None:
                value = value[:start] + value[end:]
            else:
                attr = 'password' if cat == 'P' else 'username'
                if hasattr(kpentry, attr):
                    attr = getattr(kpentry, attr)
                    value = value[:start] + \
                        (attr if attr is not None else '') + value[end:]
                else:
                    value = value[:start] + value[end:]
        return value

    def parse(self):
        """Parse Keepass KDBX3 and KDBX4 files."""
        for kpentry in self.keepass.entries:
            if self.root not in os.sep.join(filter(None, kpentry.path)):
                continue
            entry = self._getentry(kpentry)
            entry['group'] = os.path.dirname(entry.get('group', ''))

            if kpentry.history:
                for hentry in kpentry.history:
                    history = self._getentry(hentry)
                    history['group'] = os.path.join('History', entry['group'])
                    self.data.append(history)

            for att in kpentry.attachments:
                attachment = {}
                attachment['group'] = entry['group']
                attachment['title'] = att.filename
                attachment['data'] = att.data
                self.data.append(attachment)
                if entry.get('attachments', None):
                    entry['attachments'] += f", {att.filename}"
                else:
                    entry['attachments'] = att.filename
            self.data.append(entry)

    # Export methods

    def insert(self, entry):
        """Insert a password entry into KDBX encrypted vault file."""
        ignore = {'password', 'path', 'title', 'group', 'data'}
        path = os.path.join(self.root, entry.get('path'))
        title = os.path.basename(path)
        group = os.path.dirname(path)

        root_group = self.keepass.root_group
        kpgroup = self.keepass.find_groups(
            path=os.path.split(group)) if group else root_group
        if not kpgroup:
            for grp in os.path.split(group):
                # os.path.split creates an empty segment when there is nothing
                # to split, just ignore it
                if grp == '':
                    continue
                kpgroup = self.keepass.find_groups(
                    group=root_group, name=grp, first=True)
                if not kpgroup:
                    kpgroup = self.keepass.add_group(root_group, grp)
                root_group = kpgroup

        if not self.force:
            pkentry = self.keepass.find_entries(title=title, group=kpgroup,
                                                recursive=False, first=True)
            if pkentry is not None:
                raise PMError(f"An entry already exists for {path}.")

        kpentry = self.keepass.add_entry(
            destination_group=kpgroup,
            title=title,
            username=entry.pop('login', ''),
            password=entry.pop('password', ''),
            url=entry.pop('url', None),
            notes=entry.pop('comments', None),
            tags=entry.pop('tags', None),
            expiry_time=entry.pop('expiry_time', None),
            icon=entry.pop('icon', None),
            force_creation=True)

        for key, value in entry.items():
            if key in ignore:
                continue
            kpentry.set_custom_property(key, str(value))

        if 'data' in entry:
            attid = self.keepass.add_binary(entry['data'])
            kpentry.add_attachment(attid, title)

    # Context manager methods

    def open(self):
        """Open the keepass repository."""
        if not PYKEEPASS:
            raise ImportError(name='pykeepass')

        try:
            self.keepass = PyKeePass(self.prefix,
                                     password=getpassword(self.prefix),
                                     keyfile=self.keyfile)
        except (CredentialsError, PayloadChecksumError,
                HeaderChecksumError) as error:  # pragma: no cover
            raise PMError(error) from error

    def close(self):
        """Close the keepass repository."""
        self.keepass.save()

    # Format recognition methods

    def detecter_open(self):
        """Enter the tryformat context manager."""
        self.file = open(self.prefix, 'rb')

    def detecter_close(self):
        """Leave the tryformat context manager."""
        self.file.close()

    def is_format(self):
        """Return True if the file is a KDBX file."""
        sign = self.file.read(4)
        if sign != self.magic:
            return False
        return True

    def checkheader(self, header, only=False) -> bool:
        """No header check."""
        return True

    @classmethod
    def header(cls):
        """No header for KDBX file."""
        return ''


register_detecters(KDBX)
