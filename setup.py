#!/usr/bin/env python3
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.

import os
import sys

from pathlib import Path

from setuptools import setup


share = Path(sys.prefix, 'share')
base = '/usr'
if os.uname().sysname == 'Darwin':
    base = '/usr/local'
lib = Path(base, 'lib', 'password-store', 'extensions')

if '--user' in sys.argv:
    if 'PASSWORD_STORE_EXTENSIONS_DIR' in os.environ:
        lib = Path(os.environ['PASSWORD_STORE_EXTENSIONS_DIR'])
    else:
        lib = Path.home() / '.password-store' / '.extensions'
    if 'XDG_DATA_HOME' in os.environ:
        share = Path(os.environ['XDG_DATA_HOME'])
    else:
        share = Path.home() / '.local' / 'share'

setup(
    data_files=[
        (str(share / 'man' / 'man1'), [
            'share/man/man1/pass-import.1',
            'share/man/man1/pimport.1',
        ]),
        (str(share / 'bash-completion' / 'completions'), [
            'share/bash-completion/completions/pass-import',
            'share/bash-completion/completions/pimport',
        ]),
        (str(share / 'zsh' / 'site-functions'), [
            'share/zsh/site-functions/_pass-import',
            'share/zsh/site-functions/_pimport',
        ]),
        (str(lib), ["import.bash"]),
    ],
)
