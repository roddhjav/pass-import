# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import configparser
import glob
import os

from pass_import.core import Cap, register_detecters, register_managers
from pass_import.detecter import Formatter
from pass_import.errors import PMError
from pass_import.manager import PasswordImporter


class NetworkManager(Formatter, PasswordImporter):
    """Importer for Network Manager.

    :usage:
    Support import from the installed network configuration but also from a
    specific directory of NetworkManager configuration file or from a given
    file.

    Example:
    -------
    - From directory of ini file: `pass import networkmanager dir/`.
    - From ini file: `pass import networkmanager file.ini`.

    """
    cap = Cap.FORMAT | Cap.IMPORT
    name = 'network-manager'
    format = 'nm'
    url = 'https://wiki.gnome.org/Projects/NetworkManager'
    hexport = 'Also support specific networkmanager dir and ini file'
    himport = 'pass import networkmanager'
    files = []
    path = '/etc/NetworkManager/system-connections'
    keyslist = ['title', 'password', 'login', 'ssid']
    keys = {
        'title': 'connection.id',
        'password': 'wifi-security.psk',
        'login': '802-1x.identity',
        'ssid': 'wifi.ssid'
    }

    # Import method

    def parse(self):
        """Parse NetworkManager ini config file or directory."""
        keys = self.invkeys()
        keys['802-1x.password'] = 'password'
        for file in self.files:
            ini = configparser.ConfigParser()
            ini.read_file(file)
            entry = {}

            for section in ini.sections():
                for option in ini.options(section):
                    inikey = f"{section}.{option}"
                    entry[keys.get(inikey, inikey)] = ini.get(section, option,
                                                              fallback='')

            if entry.get('password', None) is not None:
                self.data.append(entry)

            file.close()

    # Context manager methods

    def exist(self):
        """Nothing to do."""
        return True

    def open(self):
        """Ini file import or dir of ini file or default dir.

        If ``self.prefix`` is a path, open it.
        If it is a path to a directory, open the files it contains
        If it is empty, import data from the default directory.

        """
        if os.path.isfile(self.prefix):
            self.files = [open(self.prefix, 'r', encoding='utf-8')]
        else:
            if self.prefix == '':
                self.prefix = self.path
            elif not os.path.isdir(self.prefix):
                raise PMError(f"{self.prefix} is neither a file nor a "
                              "directory")
            self.files = []
            for path in glob.glob(self.prefix + '/*'):
                self.files.append(open(path, 'r'))

    def close(self):
        """Close all the opened files."""
        for file in self.files:
            file.close()

    # Format recognition methods

    def is_format(self):
        """Return True if the prefix has same format than the pm."""
        try:
            for file in self.files:
                ini = configparser.ConfigParser()
                ini.read_file(file)
        except:  # noqa
            return False
        return True

    def checkheader(self, header, only=False):
        """No header check is needed."""
        return True

    @classmethod
    def header(cls):
        """No header for NetworkManager."""
        return ''


register_managers(NetworkManager)
register_detecters(NetworkManager)
