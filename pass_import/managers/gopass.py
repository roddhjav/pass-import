# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import Cap, register_detecters, register_managers
from pass_import.managers import PasswordStore


class Gopass(PasswordStore):
    """Importer & Exporter for gopass.

    If ``prefix`` is not specified in the constructor, the environment variable
    ``PASSWORD_STORE_DIR`` is required. The constructor will raise an exception
    if it is not present.

    This class supports all the environment variables supported by ''pass'',
    including ``GNUPGHOME``.

    :param dict env: Environment variables used by ``pass``.

    """
    cap = Cap.FORMAT | Cap.IMPORT | Cap.EXPORT
    name = 'gopass'
    format = 'gopass'
    command = 'gopass'
    url = 'https://www.gopass.pw/'
    himport = 'gopass import pass path/to/store'


register_managers(Gopass)
register_detecters(Gopass)
