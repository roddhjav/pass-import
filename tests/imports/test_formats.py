# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
from yaml.scanner import ScannerError

from pass_import.errors import FormatError
import tests


class TestFormats(tests.Test):
    """Ensure the parse method fail when a malformed file is given."""
    formaterror = (FormatError, AttributeError, ValueError, ScannerError,
                   TypeError)

    def test_formats(self):
        """Testing: file format for all importers."""
        ignore = ['DashlaneCSV', 'KeeperCSV', 'UPM']
        for manager in tests.conf:
            if manager in ignore or not tests.conf[manager].get('parse', True):
                continue
            with self.subTest(manager):
                _, ext = os.path.splitext(tests.conf[manager]['path'])
                prefix = os.path.join(tests.formats, 'dummy' + ext)

                with self.assertRaises(self.formaterror):
                    with tests.cls(manager, prefix) as importer:
                        importer.parse()

    def test_formats_otp(self):
        """Testing: file format for OTP based importers."""
        prefix = os.path.join(tests.db, 'andotp.json')
        with self.assertRaises(self.formaterror):
            with tests.cls('Aegis', prefix) as importer:
                importer.parse()

    def test_formats_csv(self):
        """Testing: file format for generic CSV importer."""
        prefix = os.path.join(tests.db, 'lastpass.csv')
        with self.assertRaises(self.formaterror):
            with tests.cls('GenericCSV', prefix) as importer:
                importer.cols = ''
                importer.parse()
