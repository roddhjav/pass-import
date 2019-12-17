# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

from abc import abstractmethod

import pass_import.clean as clean
from pass_import.core import Asset, Cap


class PasswordManager(Asset):
    """Interface for all password managers.

    **Manager metadata**

    :param str url: Public website of the password manager.
    :param str hexport: How to export data from the password manager.
    :param str himport: How to import data from the password manager.
    :param bool secure: A flag, to set to ``False`` if the passsword manager is
        considered not secure.

    **Set by reading settings**

    :param Action action: The current action for what the object is used.
    :param str root: Internal root where to import the passwords inside the pm.
    :param str delimiter: CSV delimiter character. Default: ``,``
    :param str cols: String that show the list of CSV expected
        columns to map columns to credential attributes. Only used for the CSV
        generic importer.

    """
    url = ''
    hexport = ''
    himport = ''
    secure = True
    keys = dict()
    keyslist = [
        'title', 'password', 'login', 'email', 'url', 'comments', 'otpauth',
        'group'
    ]

    def __init__(self, prefix=None, settings=None):
        settings = {} if settings is None else settings

        self.data = []
        self.root = settings.get('root', '')
        self.cols = settings.get('cols', '')
        self.action = settings.get('action', Cap.IMPORT)
        self.delimiter = str(settings.get('delimiter', ','))
        super(PasswordManager, self).__init__(prefix, settings)

    @classmethod
    def usage(cls):
        """Get password manager usage."""
        res = '\n'.join(cls.__doc__.split('\n')[1:-1])
        while '  ' in res:
            res = res.replace('  ', ' ')
        return res

    @classmethod
    def description(cls):
        """Get password manager description."""
        return cls.__doc__.split('\n')[0][:-1]


class PasswordImporter(PasswordManager):
    """Interface for all password managers that support importing password.

    :param list[dict] data: The list of password entries imported by the parse
        method. Each password entry is a dictionary.
    :param list keyslist: The list of core key that will be present into the
        password entry even without the extra option.
    :param dict keys: Correspondence dictionary between the password-store key
        name (``password``, ``title``, ``login``...) and the key name from the
        password manager considered.

    """
    cap = Cap.IMPORT

    @abstractmethod
    def parse(self):
        """Parse the password manager repository and retrieve passwords."""

    def invkeys(self):
        """Return the invert of ``keys``."""
        return {v: k for k, v in self.keys.items()}


class PasswordExporter(PasswordManager):
    """Interface for all password managers that support exporting password.

    **Set by reading settings**

    :param bool all: Etheir or not import all the data. Default: ``False``
    :param bool force: Either or not to force the insert if the path already
        exist. Default: ``False``

    """
    cap = Cap.EXPORT

    def __init__(self, prefix=None, settings=None):
        settings = {} if settings is None else settings
        self.all = settings.get('all', False)
        self.force = settings.get('force', False)
        super(PasswordExporter, self).__init__(prefix, settings)

    @abstractmethod
    def insert(self, entry):
        """Insert a password entry into the password repository.

        :param dict entry: The password entry to insert.
        :raises PMError: If the entry already exists or in case of
            a password manager error.
        """

    def clean(self, cmdclean, convert):
        """Clean data before export.

        **Features:**

        1. Remove unused keys and empty values.
        2. Clean protocol name in title.
        3. Clean group from unwanted value in Unix or Windows paths.
        4. Duplicate paths.

        :param bool cmdclean:
            If ``True``, make the paths more command line friendly.
        :param bool convert:
            If ``True``, convert the invalid caracters present in the paths.

        """
        for entry in self.data:
            entry = clean.unused(entry)
            path = clean.group(clean.protocol(entry.pop('group', '')))
            entry['path'] = clean.cpath(entry, path, cmdclean, convert)

        clean.dpaths(self.data, cmdclean, convert)
        clean.duplicate(self.data)
