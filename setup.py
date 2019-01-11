#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup
from pass_import import __version__

__url__ = 'https://github.com/roddhjav/pass-import'

setup(
    name="pass-import",
    version=__version__,
    author="Alexandre Pujol",
    author_email="alexandre@pujol.io",
    url=__url__,
    download_url="%s/releases/download/v%s/pass-import-%s.tar.gz"
                 % (__url__, __version__, __version__),
    description="A pass extension for importing data from most of the existing password manager.",
    license='GPL3',

    py_modules=['pass_import'],

    install_requires=[
        'defusedxml'
        ],
    tests_require=[
        'green'
        ],
    test_suite='tests',
    python_requires='>=3.4',

    keywords=[
        'password-store', 'password', 'pass', 'pass-extension',
        'password-manager', 'importer',
        ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Security :: Cryptography',
        ],
)
