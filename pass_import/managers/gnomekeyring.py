# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

try:
    import secretstorage
    SECRETSTORAGE = True
except ImportError:
    SECRETSTORAGE = False

from pass_import.core import register_managers
from pass_import.manager import PasswordImporter


class GnomeKeyring(PasswordImporter):
    """Importer & exporter for Gnome Keyring.

    :usage:
    You can provide a gnome-keyring collection label to import. It can be empty
    to import all collections.

    """
    name = 'gnome'
    format = 'libsecret'
    url = 'https://wiki.gnome.org/Projects/GnomeKeyring'
    himport = 'pass import gnome-keyring <label>'
    keys = {'login': 'account', 'url': 'host'}

    # Import method

    def parse(self):
        """Direct import from the Gnome keyring using Dbus."""
        if not SECRETSTORAGE:
            raise ImportError(name='secretstorage')

        keys = self.invkeys()
        connection = secretstorage.dbus_init()
        for collection in secretstorage.get_all_collections(connection):
            group = collection.get_label()
            if self.prefix not in ('', group):
                continue

            collection.unlock()
            for item in collection.get_all_items():
                entry = {}
                entry['group'] = group
                entry['title'] = item.get_label()
                entry['password'] = item.get_secret().decode('utf-8')
                entry['modified'] = item.get_modified()
                entry['created'] = item.get_created()
                for key, value in item.get_attributes().items():
                    entry[keys.get(key, key)] = value
                self.data.append(entry)

    # Context manager methods

    def exist(self):
        """Nothing to do."""
        return True

    @classmethod
    def isvalid(cls):
        """Nothing to do."""
        return True

    def open(self):
        """Nothing to open."""

    def close(self):
        """Nothing to close."""


register_managers(GnomeKeyring)
