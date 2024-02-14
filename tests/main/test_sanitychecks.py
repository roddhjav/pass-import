# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import tests


class TestMainSanityChecks(tests.Test):
    """Test common pass-import features and corner cases."""

    def setUp(self):
        """Ensure we run pimport, not 'pass import'."""
        os.environ['_PASSWORD_STORE_EXTENSION'] = ''  # nosec

    def test_main_help(self):
        """Testing: pimport --help."""
        cmd = ['--help']
        self.main(cmd, 0)

    def test_main_help_manager_1(self):
        """Testing: pimport --help csv."""
        cmd = ['--help', 'csv']
        self.main(cmd, 0)

    def test_main_help_manager_2(self):
        """Testing: pimport --help 1password."""
        cmd = ['--help', '1password']
        self.main(cmd, 0)

    def test_main_version(self):
        """Testing: pimport --version."""
        cmd = ['--version']
        self.main(cmd, 0)

    def test_main_list_importers(self):
        """Testing: pimport --list-importers."""
        cmd = ['--list-importers']
        self.main(cmd, 0)

    def test_main_list_exporters(self):
        """Testing: pimport --list-exporters."""
        cmd = ['--list-exporters']
        self.main(cmd, 0)

    def test_main_list_quiet(self):
        """Testing: pimport --list-importers --quiet."""
        cmd = ['--list-importers', '--quiet']
        self.main(cmd, 0)

    def test_main_list_verbose(self):
        """Testing: pimport --list-importers --verbose."""
        cmd = ['--list-importers', '--verbose']
        self.main(cmd, 0)

    def test_main_exporter_empty(self):
        """Testing: password exporter not present."""
        cmd = []
        self.main(cmd, 1, 'destination password manager not present.')

    def test_main_importer_empty(self):
        """Testing: password importer not present."""
        cmd = ['pass']
        self.main(cmd, 1, 'The source password manager or '
                          'the path to import is empty.')

    def test_main_exporter_unknown(self):
        """Testing: password exporter not supported."""
        cmd = ['not-a-manager']
        self.main(cmd, 1, 'is not a supported destination password manager.')

    def test_main_importer_unknown(self):
        """Testing: password importer not supported."""
        cmd = ['pass', 'not-a-manager', 'dummy-file']
        self.main(cmd, 1, 'is not a supported source password manager.')

    def test_main_config_file_not_valid(self):
        """Testing: configuration file not valid."""
        cmd = ['--config', tests.assets + 'format/dummy.xml']
        self.main(cmd, 1, 'configuration file not valid.')

    def test_main_no_repository(self):
        """Testing: pimport pass db/enpass.csv --out=dummy"""
        cmd = ['pass', tests.db + 'enpass.csv', '--out=dummy']
        self.main(cmd, 1, 'dummy is not a password repository.')

    def test_main_not_an_option(self):
        """Testing: pimport --not-an-option."""
        cmd = ['--not-an-option']
        self.main(cmd, 2)
