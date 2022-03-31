# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

import pass_import.auto
import tests


class TestDetect(tests.Test):
    """Test for path format detection methods."""

    def test_default(self):
        """Testing: default manager method."""
        defaults = {
            'buttercup': tests.managers.get('Buttercup'),
            'enpass': tests.managers.get('Enpass6'),
            'keepass': tests.managers.get('Keepass'),
            '1password': tests.managers.get('OnePassword8CSV'),
        }
        for name in defaults:
            with self.subTest(name):
                detect = pass_import.auto.AutoDetect(name)
                pm = detect.default()
                self.assertEqual(defaults[name], pm)

    def test_default_unknown(self):
        """Testing: default manager of an unknown manager."""
        with self.assertRaises(pass_import.ManagerError):
            detect = pass_import.auto.AutoDetect('not-a-manager')
            detect.default()

    def test_tryopen(self):
        """Testing: tryopen path method."""
        tryopen = {
            # manager: (path, (ref_tuple))
            'buttercup': (
                'buttercup.csv', (tests.managers.get('Buttercup'), [])
            ),
            'keepass': (
                'keepass.kdbx', (tests.managers.get('Keepass'), [])
            ),
        }
        for name in tryopen:
            with self.subTest(name):
                path = os.path.join(tests.db, tryopen[name][0])
                detect = pass_import.auto.AutoDetect(name)
                res = detect._tryopen(path)
                self.assertEqual(res, tryopen[name][1])

    def test_format_tryopen(self):
        """Testing: format for all managers."""
        ignore = {'AegisCipher', 'AndOTPAES'}
        for manager in tests.conf:
            if manager in ignore:
                continue
            with self.subTest(manager):
                pm = tests.managers.get(manager)
                path = os.path.join(tests.db, tests.conf[manager]['path'])
                detect = pass_import.auto.AutoDetect(pm.name)
                pm = detect.format(path)
                self.assertEqual(manager, pm.__name__)

    def test_format_default(self):
        """Testing: format from default."""
        detect = pass_import.auto.AutoDetect('keepass')
        pm = detect.format('dummy')
        self.assertEqual(pm.__name__, 'Keepass')

    def test_manager(self):
        """Testing: manager for all managers."""
        wrong_file_mode = {'SaferPass', 'ZohoCSV', 'ZohoCSVVault'}
        prefix_is_a_login = {'GnomeKeyring'}
        csv_without_header = {'DashlaneCSV', 'KeeperCSV', 'UPM'}
        not_detectables = wrong_file_mode.union(prefix_is_a_login,
                                                csv_without_header)
        identical = {
            'KeepassxcCSV': 'Keepassx2CSV', 'Keepassx2CSV': 'KeepassxcCSV',
            'GnomeAuthenticator': 'AndOTP', 'AndOTP': 'GnomeAuthenticator',
            'FigaroPM': 'Kedpm', 'Kedpm': 'FigaroPM'
        }
        ignore = {}
        for manager in tests.conf:
            if manager in ignore:
                continue
            with self.subTest(manager):
                path = os.path.join(tests.db, tests.conf[manager]['path'])
                detect = pass_import.auto.AutoDetect()
                pm = detect.manager(path)
                if manager in not_detectables:
                    self.assertEqual(pm, None)
                elif pm.format == 'kdbx':
                    self.assertTrue(pm.__name__.startswith('Keepass'))
                elif manager in identical:
                    if manager == pm.__name__:
                        self.assertEqual(manager, pm.__name__)
                    else:
                        self.assertEqual(identical[manager], pm.__name__)
                else:
                    self.assertEqual(manager, pm.__name__)
