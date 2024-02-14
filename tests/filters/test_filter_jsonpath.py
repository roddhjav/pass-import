# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.__main__ import pass_export
from pass_import.core import Cap
from pass_import.manager import PasswordImporter, PasswordExporter
from pass_import.tools import Config

import tests


class MockManager(PasswordImporter, PasswordExporter):
    """Base class for mockable based importer & exporter.

    :param dict values: Dictionary of mock values.

    """
    cap = Cap.FORMAT | Cap.IMPORT | Cap.EXPORT
    name = 'mock'
    format = 'key-value-dict'
    keys = {'login': 'username', 'comments': 'notes', 'group': 'path'}
    attributes = {
        'title', 'username', 'password', 'url', 'notes', 'icon', 'tags',
        'autotype_enabled', 'autotype_sequence', 'is_a_history_entry'
    }

    def __init__(self, prefix=None, settings=None, values=None):
        super().__init__(prefix, settings)
        self.data = values

    def insert(self, entry):
        pass

    def parse(self):
        pass

    def exist(self):
        return True

    def __enter__(self):
        return self


CONF = {

}


class TestFilter(tests.Test):
    """Test --filter features."""

    def setUp(self):
        """Setup a new keepass repository."""
        self.conf = Config()
        self.conf['droot'] = "/tmp/not/used/but/required"
        self.conf['out'] = "/tmp/not/used/but/required"
        self.conf['clean'] = False
        self.conf['convert'] = False
        self.conf['pwned'] = False
        self.conf['dry_run'] = False
        self.exporter = MockManager(self)

    def test_no_filter_on_non_empty_data_source(self):
        """Testing: export all entries without a filter provided using
         non empty data source."""
        data = [{
            'password': 'v_password',
            'login': 'v_login',
        }]
        paths_imported, paths_exported, audit = pass_export(
            self.conf, MockManager, data
        )
        self.assertTrue(len(paths_imported) == 1)
        self.assertTrue(len(paths_imported) == len(paths_exported))

    def test_no_filter_on_empty_data_source(self):
        """Testing: export all entries when no filter provided using
        empty data source."""
        data = [{}]
        paths_imported, paths_exported, audit = pass_export(
            self.conf, MockManager, data
        )
        self.assertTrue(len(paths_imported) == 1)
        self.assertTrue(len(paths_imported) == len(paths_exported))

    def test_filter_on_non_empty_data_source(self):
        """Testing: export some entries when filter provided using non
        empty data source."""
        data = [
            {
                'password': 'v_password',
                'login': 'v_login_0',
                'tags': ['Defaults']
            },
            {
                'password': 'v_password',
                'login': 'v_login_1',
                'tags': ['NotDefaults']
            },
        ]

        self.conf['filter'] = "$.entries[*].tags[?@=\"Defaults\"]"
        paths_imported, paths_exported, audit = pass_export(
            self.conf, MockManager, data
        )
        self.assertTrue(len(paths_imported) == 2)
        self.assertTrue(len(paths_exported) == 1)
        self.assertTrue(data[0]['login'] in paths_exported[0])
