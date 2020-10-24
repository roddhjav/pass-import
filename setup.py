#!/usr/bin/env python3
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.

import os
import sys
from pathlib import Path

from setuptools import setup

about = dict()
with Path('pass_import', '__about__.py').open() as file:
    exec(file.read(), about)  # nosec pylint: disable=exec-used

with open('README.md') as file:
    long_description = file.read()

share = Path(sys.prefix, 'share')
lib = Path('/usr', 'lib', 'password-store', 'extensions')
if '--user' in sys.argv:
    lib = Path.home() / '.password-store' / 'extensions'
    if 'XDG_DATA_HOME' in os.environ:
        share = Path(os.environ['XDG_DATA_HOME'])
    else:
        share = Path.home() / '.local' / 'share'

setup(
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__email__'],
    description=about['__summary__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=about['__license__'],
    url=about['__uri__'],
    packages=[
        'pass_import',
        'pass_import.decrypters',
        'pass_import.formats',
        'pass_import.managers',
    ],
    scripts=['scripts/pimport'],
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
        (str(lib), ["scripts/import.bash"]),
    ],
    install_requires=['pyaml'],
    extras_require={
        'xml': ['defusedxml'],
        'keepass': ['pykeepass'],
        'gnomekeyring': ['secretstorage'],
        'encrypted_otp': ['cryptography'],
        'decrypt': ['file-magic'],
        'all': [
            'defusedxml', 'pykeepass', 'secretstorage', 'cryptography',
            'file-magic'
        ]
    },
    python_requires='>=3.6',
    zip_safe=True,
    keywords=[
        'password-store', 'password', 'pass', 'pass-extension',
        'password-manager', 'importer'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General'
        ' Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Security :: Cryptography',
    ],
)
