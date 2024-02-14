# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#


class DecrypterError(Exception):
    """Password decrypter error."""


class FormatError(Exception):
    """Password importer format (CSV, XML, JSON or TXT) not recognized."""


class PMError(Exception):
    """Error in the execution of the password manager."""
