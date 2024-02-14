# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import shutil
from subprocess import PIPE, Popen  # nosec

from pass_import.core import register_detecters
from pass_import.detecter import Decrypter
from pass_import.errors import FormatError


class GPG(Decrypter):
    """Decrypter for GPG."""
    format = 'gpg'

    def decrypt(self):
        """Import data is GPG encrypted, let's decrypt it."""
        gpgbinary = shutil.which('gpg2') or shutil.which('gpg')
        cmd = [gpgbinary, '--with-colons', '--batch', '--decrypt', self.prefix]
        with Popen(cmd, shell=False, universal_newlines=False,
                   stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
            (stdout, stderr) = process.communicate()
            if process.wait():  # pragma: no cover
                raise FormatError(f"{stderr} {stdout}")
            return stdout.decode()[:-1]


register_detecters(GPG)
