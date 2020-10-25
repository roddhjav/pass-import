# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

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
        'autotype_enabled', 'autotype_sequence', 'path', 'is_a_history_entry'
    }

    def __init__(self, prefix=None, settings=None):
        self.keepass = None
        settings = {} if settings is None else settings
        keyfile = settings.get('key', '')
        self.keyfile = None if keyfile == '' else keyfile
        super(KDBX, self).__init__(prefix, settings)

    # Import methods

    def _getentry(self, kpentry):
        entry = dict()
        keys = self.invkeys()
        for attr in self.attributes:
            if hasattr(kpentry, attr):
                entry[keys.get(attr, attr)] = getattr(kpentry, attr)
        for key, value in kpentry.custom_properties.items():
            entry[key] = value
        return entry

    def parse(self):
        """Parse Keepass KDBX3 and KDBX4 files."""
        for kpentry in self.keepass.entries:
            if self.root not in kpentry.path:
                continue
            entry = self._getentry(kpentry)
            entry['group'] = os.path.dirname(entry['group'])

            if kpentry.history:
                for hentry in kpentry.history:
                    history = self._getentry(hentry)
                    history['group'] = os.path.join('History', entry['group'])
                    self.data.append(history)

            for att in kpentry.attachments:
                attachment = dict()
                attachment['group'] = entry['group']
                attachment['title'] = att.filename
                attachment['data'] = att.data
                self.data.append(attachment)
                if entry.get('attachments', None):
                    entry['attachments'] += ", %s" % att.filename
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
        kpgroup = self.keepass.find_groups(path=group)
        if not kpgroup:
            for grp in group.split('/'):
                kpgroup = self.keepass.find_groups(path=grp)
                if not kpgroup:
                    kpgroup = self.keepass.add_group(root_group, grp)
                root_group = kpgroup

        if not self.force:
            pkentry = self.keepass.find_entries(title=title, group=kpgroup,
                                                recursive=False, first=True)
            if pkentry is not None:
                raise PMError("An entry already exists for %s." % path)

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
            raise PMError(error)

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

    def checkheader(self, header, only=False):
        """No header check."""
        return True

    @classmethod
    def header(cls):
        """No header for KDBX file."""
        return ''


register_detecters(KDBX)
