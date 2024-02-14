# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
from typing import Dict
from abc import abstractmethod

from pass_import import clean
from pass_import.audit import Audit
from pass_import.core import Asset, Cap


class PasswordManager(Asset):
    """Interface for all password managers.

    **Manager metadata**

    :param str url: Public website of the password manager.
    :param str hexport: How to export data from the password manager.
    :param str himport: How to import data from the password manager.
    :param bool secure: A flag, to set to ``False`` if the password manager is
        considered not secure.

    **Set by reading settings**

    :param Action action: The current action for what the object is used.
    :param str root: Internal root where to import the passwords inside the pm.
    :param str delimiter: CSV delimiter character. Default: ``,``
    :param str cols: String that shows the list of CSV expected
        columns to map columns to credential attributes. Only used for the CSV
        generic importer.

    """
    url = ''
    hexport = ''
    himport = ''
    secure = True
    keys: Dict[str, str] = {}
    keyslist = [
        'title', 'password', 'login', 'email', 'url', 'comments', 'otpauth',
        'group'
    ]

    def __init__(self, prefix=None, settings=None):
        settings = {} if settings is None else settings

        self.data: Dict[str, str] = []
        self.root = settings.get('root', '')
        self.cols = settings.get('cols', '')
        self.action = settings.get('action', Cap.IMPORT)
        self.delimiter = str(settings.get('delimiter', ','))
        super().__init__(prefix)

    @classmethod
    def usage(cls) -> str:
        """Get password manager usage."""
        res = '\n'.join(cls.__doc__.split('\n')[1:-1])
        if ':usage:' in res:
            res = res.split(':usage:')[1]
            while '  ' in res:
                res = res.replace('  ', ' ')
            return res
        return ''

    @classmethod
    def description(cls) -> str:
        """Get password manager description."""
        return cls.__doc__.split('\n', maxsplit=1)[0]


class PasswordImporter(PasswordManager):
    """Interface for all password managers that support importing passwords.

    :param list[dict] data: The list of password entries imported by the parse
        method. Each password entry is a dictionary.
    :param list keyslist: The list of core key that will be present into the
        password entry, even without the extra option.
    :param dict keys: Correspondence dictionary between the password-store key
        name (``password``, ``title``, ``login``...), and the key name from the
        password manager considered.

    """
    cap = Cap.IMPORT

    @abstractmethod
    def parse(self):
        """Parse the password manager repository and retrieve passwords."""

    def invkeys(self) -> Dict[str, str]:
        """Return the invert of ``keys``."""
        return {v: k for k, v in self.keys.items()}

    def _sortgroup(self, folders: Dict[str, Dict[str, str]]):
        """Order groups in ``data``.

        :param dict folders: The group structure, it must be generated
            as follow:
                folders['<group-id>'] = {
                    'group': '<name>',
                    'parent': '<parent-id>'
                }
        """
        for folder in folders.values():
            parentid = folder.get('parent', '')
            parentname = folders.get(parentid, {}).get('group', '')
            folder['group'] = os.path.join(parentname, folder.get('group', ''))

        for entry in self.data:
            groupid = entry.get('group', '')
            entry['group'] = folders.get(groupid, {}).get('group', '')


class PasswordExporter(PasswordManager):
    """Interface for all password managers that support exporting passwords.

    **Set by reading settings**

    :param bool all: Ethier or not import all the data. Default: ``False``
    :param bool force: Either or not to force the insert if the path already
        exist. Default: ``False``

    """
    cap = Cap.EXPORT

    def __init__(self, prefix=None, settings=None):
        settings = {} if settings is None else settings
        self.all = settings.get('all', False)
        self.force = settings.get('force', False)
        super().__init__(prefix, settings)

    @abstractmethod
    def insert(self, entry: Dict[str, str]):
        """Insert a password entry into the password repository.

        :param dict entry: The password entry to insert.
        :raises PMError: If the entry already exists or in case of
            a password manager error.
        """

    def clean(self, cmdclean: bool, convert: bool):
        """Clean data before export.

        **Features:**

        1. Remove unused keys and empty values.
        2. Clean the protocol's name in the title.
        3. Clean group from unwanted values in Unix or Windows paths.
        4. Duplicate paths.
        5. Format the One-Time Password (OTP) url.

        :param bool cmdclean:
            If ``True``, make the paths more command line friendly.
        :param bool convert:
            If ``True``, convert the invalid characters present in the paths.

        """
        for entry in self.data:
            entry = clean.unused(entry)
            path = clean.group(clean.protocol(entry.pop('group', '')))
            entry['path'] = clean.cpath(entry, path, cmdclean, convert)

        clean.dpaths(self.data, cmdclean, convert)
        clean.dpaths(self.data, cmdclean, convert)
        clean.duplicate(self.data)
        clean.otp(self.data)

    def audit(self, hibp: bool = False):
        """Audit the parsed password for vulnerable passwords.

        **Features:**

        1. Look for breached password from haveibeenpwned.com,
        2. Check for duplicated passwords,
        3. Check password strength estimaton using zxcvbn.

        :param bool hibp: A flag, to set to ``True`` to look for breached
            password from haveibeenpwned.com
        :returns dict: A report dict.

        """
        audit = Audit(self.data)
        if hibp:
            audit.password()
        audit.zxcvbn()
        audit.duplicates()
        return audit.report
