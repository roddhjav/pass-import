# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import shutil
from pathlib import Path

from pass_import.core import Cap, register_detecters, register_managers
from pass_import.detecter import Formatter
from pass_import.errors import FormatError, PMError
from pass_import.formats.cli import CLI


class PasswordStore(CLI, Formatter):
    """Importer & Exporter for password-store.

    If ``prefix`` is not specified in the constructor, the environment variable
    ``PASSWORD_STORE_DIR`` is required. The constructor will raise an exception
    if it is not present.

    This class supports all the environment variables supported by ''pass'',
    including ``GNUPGHOME``.

    :param dict env: Environment variables used by ``pass``.

    """
    cap = Cap.FORMAT | Cap.IMPORT | Cap.EXPORT
    name = 'pass'
    format = 'pass'
    command = 'pass'
    url = 'https://passwordstore.org'
    himport = 'pass import pass path/to/store'

    def __init__(self, prefix=None, settings=None):
        self._gpgbinary = shutil.which('gpg2') or shutil.which('gpg')
        super().__init__(prefix, settings)
        self._setenv('PASSWORD_STORE_DIR')
        self._setenv('PASSWORD_STORE_KEY')
        self._setenv('PASSWORD_STORE_GIT', 'GIT_DIR')
        self._setenv('PASSWORD_STORE_GPG_OPTS')
        self._setenv('PASSWORD_STORE_X_SELECTION', 'X_SELECTION')
        self._setenv('PASSWORD_STORE_CLIP_TIME', 'CLIP_TIME')
        self._setenv('PASSWORD_STORE_UMASK')
        self._setenv('PASSWORD_STORE_GENERATED_LENGTH', 'GENERATED_LENGTH')
        self._setenv('PASSWORD_STORE_CHARACTER_SET', 'CHARACTER_SET')
        self._setenv('PASSWORD_STORE_CHARACTER_SET_NO_SYMBOLS',
                     'CHARACTER_SET_NO_SYMBOLS')
        self._setenv('PASSWORD_STORE_ENABLE_EXTENSIONS')
        self._setenv('PASSWORD_STORE_EXTENSIONS_DIR', 'EXTENSIONS')
        self._setenv('PASSWORD_STORE_SIGNING_KEY')
        self._setenv('GNUPGHOME')

        if prefix:
            self.prefix = prefix
        if 'PASSWORD_STORE_DIR' not in self.env or self.prefix is None:
            raise PMError(f"{self.name} prefix unknown")

    @property
    def prefix(self):
        """Get password store prefix from PASSWORD_STORE_DIR."""
        return self.env['PASSWORD_STORE_DIR']

    @prefix.setter
    def prefix(self, value):
        self.env['PASSWORD_STORE_DIR'] = value

    # Import methods

    def list(self, path=''):
        """List the paths in the password store repository.

        :param str path: Root path to the password repository to list.
        :return list: Return the list of paths in a store.

        """
        prefix = Path(self.prefix) / path
        if Path(str(prefix) + '.gpg').is_file():
            paths = [path]
        else:
            paths = []
            hiddens = []
            for ppath in prefix.rglob('.*'):
                if ppath.is_dir():
                    hiddens.extend(list(ppath.rglob('*.gpg')))
                else:
                    hiddens.append(ppath)
            for ppath in prefix.rglob('*.gpg'):
                if ppath in hiddens:
                    continue
                passname = ppath.relative_to(self.prefix).with_suffix('')
                paths.append(str(passname))
        paths.sort()
        return paths

    def show(self, path):
        """Decrypt path and read the credentials in the password file.

        :param str path: Path to the password entry to decrypt.
        :return dict: Return a dictionary with of the password entry.
        :raise PMError: If path not in the store.
        """
        entry = {}
        entry['group'] = os.path.dirname(path)
        entry['title'] = os.path.basename(path)
        try:
            data = self._command(['show', path]).split('\n')
        except UnicodeDecodeError:
            entry['data'] = self._command(['show', path], nline=False)
            return entry

        data.pop()
        if data:
            line = data.pop(0)
            if ': ' in line:
                (key, value) = line.split(': ', 1)
                entry[key] = value
            else:
                entry['password'] = line
        for line in data:
            if ': ' in line:
                (key, value) = line.split(': ', 1)
                entry[key] = value
            elif line.startswith('otpauth://'):
                entry['otpauth'] = line
            elif 'comments' in entry:
                entry['comments'] += '\n' + line
        return entry

    def parse(self):
        """Parse a password-store repository."""
        paths = self.list()
        if not paths:
            raise FormatError('empty password store.')
        for path in paths:
            if self.root not in path:
                continue
            try:
                entry = self.show(path)
            except PMError as error:  # pragma: no cover
                raise FormatError(error) from error
            self.data.append(entry)

    # Export methods

    def insert(self, entry):
        """Insert a password entry into the password repository.

        :param dict entry: The password entry to insert.
        :raises PMError: If the entry already exists or in case
            of a password manager error.

        The entry is converted into the following format:

        .. code-block:: console

            <password>
            <key>: <value>

        If ``PasswordManager.all`` is true, all the entry values are printed.
        Otherwise, only the key present in ``PasswordManager.keyslist`` are
        printed following the order from this list. The title, path, and group
        keys are ignored.

        If ``PasswordManager.force`` is true, it will overwrite previous entry.

        If the 'data' key is present, the entry is considered as a binary
        attachment and return the binary data.

        """
        path = os.path.join(self.root, entry.get('path'))
        if not self.force:
            if os.path.isfile(os.path.join(self.prefix, path + '.gpg')):
                raise PMError(f"An entry already exists for {path}.")

        if 'data' in entry:
            data = entry['data']
        else:
            seen = {'password', 'path', 'title', 'group'}
            data = entry.get('password', '') + '\n'
            for key in self.keyslist:
                if key in seen:
                    continue
                if key in entry:
                    if 'otpauth' in key:
                        data += f"{entry.get(key)}\n"
                    else:
                        data += f"{key}: {entry.get(key)}\n"
                seen.add(key)

            if self.all:
                for key, value in entry.items():
                    if key in seen:
                        continue
                    data += f"{key}: {value}\n"

        arg = ['insert', '--multiline', '--force', '--', path]
        return self._command(arg, data)

    # Context manager methods

    def exist(self):
        """Check if the password store is initialized.

        :return bool:
            ``True`` if the password store is initialized, ``False`` otherwise.
        """
        return os.path.isfile(os.path.join(self.prefix, '.gpg-id'))

    # pylint: disable=arguments-differ
    def isvalid(self):
        """Ensure the GPG keyring is usable.

        This function ensures that:

        - All the public gpgids are present in the keyring.
        - All the public gpgids are trusted enough.
        - At least one private key is present in the keyring.

        :return bool:
            ``True`` or ``False`` either or not the GPG keyring is usable.
        """
        trusted = ['m', 'f', 'u', 'w', 's']
        with open(os.path.join(self.prefix, '.gpg-id'), 'r') as file:
            gpgids = file.read().split('\n')
            if gpgids[len(gpgids) - 1] == '':
                gpgids.pop()

        cmd = [
            self._gpgbinary,
            '--with-colons',
            '--batch',
            '--list-keys',
            '--',
        ]
        for gpgid in gpgids:
            res, out, _ = self._call(cmd + [gpgid])
            if res:
                return False
            for line in out.split('\n'):
                record = line.split(':')
                if record[0] == 'pub':
                    trust = record[1]
            if trust not in trusted:
                return False

        cmd = [
            self._gpgbinary,
            '--with-colons',
            '--batch',
            '--list-secret-keys',
            '--',
        ]
        for gpgid in gpgids:
            res, _, _ = self._call(cmd + [gpgid])
            if res == 0:
                return True
        return False

    def open(self):
        """Ensure prefix is a path to a password repository."""
        if not os.path.isdir(self.prefix):
            raise PMError(f"{self.prefix} is not a password repository.")

    def close(self):
        """There is no file to close."""

    # Format recognition methods

    def is_format(self):
        """Ensure the prefix is a directory than contain a .gpg-id file."""
        if os.path.isdir(self.prefix):
            path = os.path.join(self.prefix, '.gpg-id')
            if os.path.isfile(path):
                return True
        return False

    def checkheader(self, header, only=False):
        """No header check is needed."""
        return True

    @classmethod
    def header(cls):
        """No header for pass."""
        return ''


register_managers(PasswordStore)
register_detecters(PasswordStore)
