# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.decrypters.gpg import GPG
import tests


class TestDecrypter(tests.Test):
    """Test for Decrypter classes."""

    def test_gpg(self):
        """Testing: decrypter GPG."""
        with open(os.path.join(tests.db, 'lastpass.csv'), 'r') as file:
            ref = file.read()
            ref = ref[:-1]

        with GPG(os.path.join(tests.db, 'lastpass.csv.gpg')) as file:
            plain = file.decrypt()

        self.assertEqual(plain, ref)
