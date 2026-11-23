# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import pass_import
import tests
from pass_import.core import Cap


class TestManagers(tests.Test):
    """Test the Managers and Detecters classes."""

    def test_get_format_version(self):
        """Testing: get a manager from its name, format and version."""
        pm = tests.managers.get('keepass', 'xml', '')
        self.assertEqual(pm.__name__, 'KeepassXML')

    def test_get_unknown(self):
        """Testing: get an unknown manager."""
        with self.assertRaises(pass_import.ManagerError):
            tests.managers.get('not-a-manager')

    def test_detecters_invalid_cap(self):
        """Testing: detecters with an unsupported capability."""
        with self.assertRaises(pass_import.ManagerError):
            pass_import.Detecters(Cap.IMPORT)
