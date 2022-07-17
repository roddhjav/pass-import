# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2022 Stefan Marsiske <sphinx@ctrlc.hu>.
#

import urllib

try:
    from pwdsphinx import sphinx
    PWDSPHINX = True
except ImportError:
    PWDSPHINX = False

from pass_import.core import Cap#, register_detecters
#from pass_import.detecter import Formatter
from pass_import.manager import PasswordExporter
from pass_import.errors import PMError
from pass_import.tools import getpassword
from pass_import.core import register_managers



class Sphinx(PasswordExporter):
    """Exporter for Sphinx.
       This exporter requires pwdsphinx to run.
    """
    name = 'sphinx'
    default = True
    url = 'https://github.com/stef/pwdsphinx/'
    cap = Cap.EXPORT
    name = 'sphinx'
    reused = {}
    weak = 0

    def exist(self):
        """Nothing to do."""
        return True

    # Export methods
    def insert(self, entry):
        """Insert a password entry into sphinx."""

        if entry.pop('is_a_history_entry', False):
            raise PMError(f"Skipping historical '{entry['path']}'")
        pwd=entry.pop('password', '')
        if not pwd:
            raise PMError(f"Skipping empty password '{entry['path']}'")
        user=entry.pop('login', '')
        if not user:
            raise PMError(f"Skipping '{entry['path']}' has no user")
        url = entry.pop('url', None)
        if url:
            url = urllib.parse.urlparse(url)
            host= f"{url.hostname}"
            if url.port:
                host=f"{host}:{url.port}"
        else:
            host = entry.pop('path','')
        #print("user", user, "host", host, "pwd", pwd)

        q = sphinx.zxcvbn(pwd)
        if q['score']<4:
            self.weak+=1
            print(f"Password for {user}@{host} is weak consider changing it asap with sphinx.")
            #print(q)
        if pwd in self.reused:
            print(f"Password for {user}@{host} is reused also for:")
            for id in self.reused[pwd]:
                print(f"\t{id}")
            self.reused[pwd].append(f"{user}@{host}")
        else:
            self.reused[pwd]=[f"{user}@{host}"]

        try: sphinx.bin2pass.pass2bin(pwd, None)
        except OverflowError:
            raise PMError(f"Failed to import password for {user}@{host} to sphinx: too big.")

        s = sphinx.connect()
        try:
            sphinx.create(s, self.masterpass, user, host, target=pwd)
        except:
            raise PMError(f"Failed to export {user}@{host} to sphinx.")
        s.close()

    # Context manager methods

    def open(self):
        if not PWDSPHINX:
            raise ImportError(name='pwdsphinx')
        self.masterpass = getpassword("sphinx").encode('utf8')

    def close(self):
        self.masterpass = None
        if self.weak>0:
            print(f"exported {self.weak} weak passwords")
        reused = sum(1 for id in self.reused.values() if len(id)>1)
        if reused > 0:
            print(f"exported {reused} password which were not unique")
        self.reused = {}

register_managers(Sphinx)
