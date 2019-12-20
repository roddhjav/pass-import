# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.errors import PMError
from pass_import.managers.keepass import Keepass
from pass_import.managers.passwordstore import PasswordStore
from pass_import.managers.networkmanager import NetworkManager
import tests


class TestOpen(tests.Test):
    """Test the open & close method of some managers."""

    # Multiple manager tests

    def test_open(self):
        """Testing: open method for some managers."""
        for pm in [PasswordStore, Keepass, NetworkManager]:
            with self.assertRaises(PMError) as _:
                with pm('dummy') as _:
                    pass

    # Single manager tests

    def test_open_networkmanager(self):
        """Testing: open method for networkmanager."""
        for prefix in ['', os.path.join(tests.db, 'networkmanager/eduroam')]:
            with NetworkManager(prefix) as _:
                pass
