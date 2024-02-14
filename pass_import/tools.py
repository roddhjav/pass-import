# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import getpass
import os
import sys
from typing import Tuple, Dict, Union

try:
    import magic
    MAGIC = True
except ImportError:
    MAGIC = False

import yaml

from pass_import import clean
from pass_import.core import Cap


def getpassword(path, name='Password') -> str:
    """Get the master password."""
    return getpass.getpass(f"{name} for {path}: ")


def get_magics(path) -> Tuple[str, str]:
    """Get file format and encoding.

    The magic library is not really good at detecting text file-based format
    like CSV, JSON, YAML or, XML so we only use it to detect binary format and
    the encoding.

    Support both file-magic and python-magic as both are shipped under the same
    name in various distributions.

    """
    if not MAGIC:
        return None, None

    with open(path, 'rb') as file:
        header = file.read(2048)

    if hasattr(magic, 'detect_from_content'):  # file-magic
        res = magic.detect_from_content(header)
        mime_type = res.mime_type
        magic_name = res.name
    else:  # python-magic
        mime_type = magic.from_buffer(header, mime=True)
        magic_name = magic.from_buffer(header)

    mime_to_format = {
        'application/pgp': 'gpg',
        'application/x-sqlite3': 'sqlite3'
    }
    name_to_format = {'KDBX': 'kdbx', 'openssl': 'openssl', 'PGP': 'gpg'}

    frmt = mime_to_format.get(mime_type, None)
    for name, plain_format in name_to_format.items():
        if name in magic_name:
            frmt = plain_format

    encoding = None
    if 'UTF-8 Unicode (with BOM)' in magic_name:
        encoding = 'utf-8-sig'

    return frmt, encoding


class Config(dict):
    """Manage configuration, settings, and output messages.

    **Order of precedence of the settings:**

    1. Program options,
    2. Config file,
    3. Default values.

    :param bool passwordstore: If ``True`` consider pass-import is run as
        the password-store extension. Use :func:`~currate` to preset
        password-store settings.
    :param int verb:
        Set the verbosity mode:

        - ``0`` No verbose output,
        - ``1`` Default verbose, enable :func:`~verbose`,
        - ``2`` Enable :func:`~show`,
        - ``3`` Enable :func:`~debug`.
    :param bool quiet: If ``True`` suppress all non-error messages. Takes
        precedence over ``verbose``.

    """
    # Normal colors
    green = '\033[32m'
    yellow = '\033[33m'
    magenta = '\033[35m'
    end = '\033[0m'

    # Bold colors
    RED = '\033[1m\033[91m'
    GREEN = '\033[1m\033[92m'
    YELLOW = '\033[1m\033[93m'
    MAGENTA = '\033[1m\033[95m'
    BOLD = '\033[1m'

    def __init__(self):
        defaults = {'delimiter': ',', 'decrypted': False}
        super().__init__(defaults)
        self.verb = 0
        self.quiet = False

        self.passwordstore = bool(
            os.environ.get('_PASSWORD_STORE_EXTENSION', '') == 'import')

    def verbosity(self, verbose=0, quiet=False):
        """Set program verbosity."""
        self.verb = verbose
        self.quiet = quiet
        if self.quiet:
            self.verb = 0

    def readconfig(self, args: Dict[str, str]):
        """Read and merge config from args, config file and default."""
        configs = {}
        if os.path.isfile(args.get('config', '')):
            configpath = args['config']
        elif self.passwordstore:
            configpath = os.path.join(os.environ.get('PASSWORD_STORE_DIR', ''),
                                      '.import')
        else:
            configpath = '.import'

        if os.path.isfile(configpath):
            with open(configpath, 'r') as file:
                configs = yaml.safe_load(file)

        filter_file = args.get('filter', None)
        if filter_file is not None and os.path.isfile(filter_file):
            with open(filter_file, mode='r') as f:
                args['filter'] = f.read()

        self.merge(configs)
        self.merge(args)
        self.setclean()

    def setclean(self):
        """Set the cleaning variables."""
        cleaning = ['separator', 'cleans', 'protocols', 'invalids']
        for key in cleaning:
            if key in self:
                setattr(clean, key.upper(), self[key])

        if 'separator' in self:
            clean.CLEANS[' '] = self['separator']

    def currate(self):
        """Generate curated config from pass-import and pimport arguments."""
        self['exporter'] = self.pop('dst', '')
        if self.passwordstore:
            self['exporter'] = 'pass'
            self['out'] = os.environ['PASSWORD_STORE_DIR']
            self['list_importers'] = self.get('list', False)
            self['list_exporters'] = False

    def getsettings(self, root='', action=Cap.IMPORT
                    ) -> Dict[str, Union[str, bool]]:
        """Return a curated setting dict for use in a manager class."""
        settings = {'action': action, 'root': root}
        keep = {
            'all', 'force', 'delimiter', 'cols', '1password', 'lastpass',
            'key', 'decrypted'
        }
        for key in self:
            if key in keep:
                settings[key] = self[key]
        return settings

    def merge(self, other):
        """Update the dictionary only if the value is not null."""
        for key, value in other.items():
            if value is not None:
                self[key] = value

    def show(self, entry):
        """Show a password entry."""
        if self.verb >= 2:
            ignore = {'data', 'password', 'title', 'group', 'path'}
            path = os.path.join(self.get('droot', ''), entry.get(
                'path', entry.get('title', '')))
            self.verbose("Path", path)
            res = entry.get('password', '') + '\n'
            for key, value in entry.items():
                if key in ignore:
                    continue
                res += f"{key}: {value}\n"
            self.verbose("Data", res.replace('\n', '\n           '))

    def verbose(self, title='', msg=''):
        """Verbose method, takes title and msg. msg can be empty."""
        if self.verb >= 1 and msg == '':
            out = (f"{self.MAGENTA}  .  {self.end}{self.magenta}"
                   f"{title}{self.end}")
            print(out, file=sys.stdout)
        elif self.verb >= 1:
            out = (f"{self.MAGENTA}  .  {self.end}{self.magenta}"
                   f"{title}: {self.end}{msg}")
            print(out, file=sys.stdout)

    def debug(self, title='', msg=''):
        """Debug method."""
        if self.verb >= 3:
            self.verbose(title, msg)

    def message(self, msg=''):
        """Message method."""
        if not self.quiet:
            out = f"{self.BOLD}  .  {self.end}{msg}"
            print(out, file=sys.stdout)

    def echo(self, msg=''):
        """Echo a message after a tab."""
        if not self.quiet:
            print(f"\t{msg}", file=sys.stdout)

    def success(self, msg=''):
        """Success method."""
        if not self.quiet:
            out = f"{self.GREEN} (*) {self.end}{self.green}{msg}{self.end}"
            print(out, file=sys.stdout)

    def warning(self, msg=''):
        """Warning method."""
        if not self.quiet:
            out = f"{self.YELLOW}  w  {self.end}{self.yellow}{msg}{self.end}"
            print(out, file=sys.stdout)

    def error(self, msg=''):
        """Error method."""
        err = f"{self.RED} [x] {self.end}{self.BOLD}Error: {self.end}{msg}"
        print(err, file=sys.stderr)

    def die(self, msg=''):
        """Show an error and exit the program."""
        self.error(msg)
        sys.exit(1)
