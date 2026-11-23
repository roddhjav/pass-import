# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import io
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
        for name, expected in defaults.items():
            with self.subTest(name):
                detect = pass_import.auto.AutoDetect(name)
                pm = detect.default()
                self.assertEqual(expected, pm)

    def test_default_unknown(self):
        """Testing: default manager of an unknown manager."""
        with self.assertRaises(pass_import.ManagerError):
            detect = pass_import.auto.AutoDetect('not-a-manager')
            detect.default()

    def test_default_name(self):
        """Testing: default manager from a name given to the method."""
        detect = pass_import.auto.AutoDetect()
        pm = detect.default('keepass')
        self.assertEqual(pm, tests.managers.get('Keepass'))

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

    def test_format_unknown(self):
        """Testing: format falls back on the only untestable format."""
        detect = pass_import.auto.AutoDetect('lastpass')
        pm = detect.format(tests.db + 'keepass.xml')
        self.assertEqual(pm.__name__, 'LastpassCLI')

    def test_format_stream(self):
        """Testing: format of decrypted plain data."""
        with open(tests.db + 'lastpass.csv') as file:
            plain = file.read()
        detect = pass_import.auto.AutoDetect(
            'lastpass', settings={'decrypted': True})
        pm = detect.format(plain)
        self.assertEqual(pm.__name__, 'LastpassCSV')

    def test_manager_stream(self):
        """Testing: manager of decrypted plain data."""
        with open(tests.db + 'lastpass.csv') as file:
            plain = file.read()
        detect = pass_import.auto.AutoDetect(settings={'decrypted': True})
        pm = detect.manager(plain)
        self.assertEqual(pm.__name__, 'LastpassCSV')

    def test_manager(self):
        """Testing: manager for all managers."""
        wrong_file_mode = {'SaferPass', 'SynologyC2CSV', 'ZohoCSV', 'ZohoCSVVault'}
        prefix_is_a_login = {'GnomeKeyring', 'BitwardenCLI', 'OnePasswordCLI',
                             'LastpassCLI'}
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

    def test_csv_json_line(self):
        """Testing: a JSON formatted line is not a CSV file."""
        lines = [
            '{"uuid":"a","title":"t"}\n{"uuid":"b","title":"u"}\n',
            '\ufeff{"uuid":"a","tags":["x","y"],"title":"a, b"}\n',
        ]
        pm = tests.managers.get('OnePassword8CSV')
        for line in lines:
            with self.subTest(line), pm(io.StringIO(line)) as importer:
                self.assertFalse(importer.is_format())
        with pm(os.path.join(tests.db, '1password.1pif')) as importer:
            self.assertFalse(importer.is_format())

    def test_manager_stream_unknown(self):
        """Testing: unknown decrypted plain data is not detected."""
        detect = pass_import.auto.AutoDetect(settings={'decrypted': True})
        self.assertIsNone(detect.manager('foo,bar\n1,2\n'))

    def test_applekeychain_plain_text(self):
        """Testing: plain text is not an Apple keychain file."""
        pm = tests.managers.get('AppleKeychain')
        for text in ('hello world\nfoo\n', ''):
            with self.subTest(text), pm(io.StringIO(text)) as importer:
                self.assertFalse(importer.is_format())
