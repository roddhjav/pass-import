# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

from unittest import mock

import pass_import.audit
import tests


REFERENCE_AUDIT = tests.yaml_load('audit.yml')


def getpath(root):
    """Get data from the reference audit repository."""
    data = []
    for entry in REFERENCE_AUDIT:
        if entry['group'] in root:
            data.append(entry)
    return data


class TestPwnedAPI(tests.Test):
    """Test the PwnedAPI class."""

    def setUp(self):
        self.api = pass_import.audit.PwnedAPI()

    @mock.patch('requests.get', tests.mock_hibp)
    def test_password_range(self):
        """Testing: https://api.haveibeenpwned.com/range API."""
        prefix = '21BD1'
        phash = '21BD12DC183F740EE76F27B78EB39C8AD972A757'
        hashes, counts = self.api.password_range(prefix)
        self.assertIn(phash, hashes)
        self.assertTrue(counts[hashes.index(phash)] == 52579)
        self.assertTrue(len(hashes) == len(counts))
        self.assertTrue(len(hashes) == 11)


class TestAudit(tests.Test):
    """Test the Audit class."""
    passwords_nb = 7

    @mock.patch('requests.get', tests.mock_hibp)
    def test_password_notpwned(self):
        """Testing: audit for password not breached with K-anonymity."""
        data = getpath('Password/notpwned')
        audit = pass_import.audit.Audit(data)
        audit.password()
        self.assertTrue(len(audit.breached) == 0)

    @mock.patch('requests.get', tests.mock_hibp)
    def test_password_pwned(self):
        """Testing: pass audit for password breached with K-anonymity."""
        ref_counts = [52579, 3, 120, 1386, 3730471, 123422, 411]
        data = getpath('Password/pwned')
        audit = pass_import.audit.Audit(data)
        audit.password()
        self.assertTrue(len(audit.breached) == self.passwords_nb)
        idx = 0
        for password, count in audit.breached:
            self.assertTrue(data[idx]['password'] == password)
            self.assertTrue(ref_counts[idx] == count)
            idx += 1

    def test_zxcvbn_weak(self):
        """Testing: audit for weak password with zxcvbn."""
        data = [{
            'path': 'Password/pwned/1',
            'password': 'P@ssw0rd',
            'group': 'Password/pwned'
        }]
        audit = pass_import.audit.Audit(data)
        audit.zxcvbn()
        self.assertTrue(len(audit.weak) == 1)
        self.assertTrue(audit.weak[0][1]['score'] == 0)

    def test_zxcvbn_strong(self):
        """Testing: audit for strong password with zxcvbn."""
        data = getpath('Password/good')
        audit = pass_import.audit.Audit(data)
        audit.zxcvbn()
        self.assertTrue(len(audit.weak) == 0)

    def test_duplicates_yes(self):
        """Testing: audit for duplicates password."""
        data = getpath('Password/notpwned/1')
        data.append(data[0])
        audit = pass_import.audit.Audit(data)
        audit.duplicates()
        self.assertTrue(len(audit.duplicated) == 1)

    def test_duplicates_no(self):
        """Testing: audit for not duplicated password."""
        data = getpath('Password/notpwned/')
        audit = pass_import.audit.Audit(data)
        audit.duplicates()
        self.assertTrue(len(audit.duplicated) == 0)

    def test_empty(self):
        """Testing: audit for empty password."""
        data = [{'password': ''}]
        audit = pass_import.audit.Audit(data)
        audit.zxcvbn()
        audit.password()
        audit.duplicates()
        self.assertTrue(len(audit.weak) == 0)
        self.assertTrue(len(audit.breached) == 0)
        self.assertTrue(len(audit.duplicated) == 0)
