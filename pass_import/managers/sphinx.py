# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2022 Stefan Marsiske <sphinx@ctrlc.hu>.
# Copyright (C) 2022 Alexandre PUJOL <alexandre@pujol.io>.
#

import urllib

try:
    from pwdsphinx import sphinx
    PWDSPHINX = True
except ImportError:
    PWDSPHINX = False

from pass_import.core import register_managers
from pass_import.errors import PMError
from pass_import.manager import PasswordExporter
from pass_import.tools import getpassword


class Sphinx(PasswordExporter):
    """Exporter for Sphinx."""
    name = 'sphinx'
    default = True
    url = 'https://github.com/stef/pwdsphinx/'

    # Export methods

    def insert(self, entry):
        """Insert a password entry into Sphinx."""
        if entry.pop('is_a_history_entry', False):
            raise PMError(f"Skipping historical '{entry['path']}'")
        pwd = entry.pop('password', '')
        if not pwd:
            raise PMError(f"Skipping empty password '{entry['path']}'")
        user = entry.pop('login', '')
        if not user:
            raise PMError(f"Skipping '{entry['path']}' has no user")
        url = entry.pop('url', None)
        if url:
            url = urllib.parse.urlparse(url)
            host = f"{url.hostname}"
            if url.port:
                host = f"{host}:{url.port}"
        else:
            host = entry.pop('path', '')
        # print("user", user, "host", host, "pwd", pwd)

        try:
            sphinx.bin2pass.pass2bin(pwd, None)
        except OverflowError:
            raise PMError(f"Failed to import password for {user}@{host}"
                          " to sphinx: password too long.")

        s = sphinx.connect()
        try:
            sphinx.create(s, self.masterpassword, user, host, target=pwd)
        except Exception:
            raise PMError(f"Failed to export {user}@{host} to sphinx.")
        s.close()

    # Context manager methods

    def exist(self):
        """Nothing to do."""
        return True

    def open(self):
        """Get Sphinx master password."""
        if not PWDSPHINX:
            raise ImportError(name='pwdsphinx')
        self.masterpassword = getpassword("sphinx").encode('utf8')

    def close(self):
        """Forget Sphinx master password."""
        self.masterpassword = None


register_managers(Sphinx)
