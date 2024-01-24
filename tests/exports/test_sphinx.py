# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 20220 Stefan Marsiske <sphinx@ctrlc.hu>.
#

from unittest.mock import patch

import tests
from pass_import.errors import PMError
from pass_import.managers.sphinx import Sphinx

try:
    from pwdsphinx import sphinx as pwdsphinx
    from pwdsphinx.sphinx import RULE_SIZE
except ImportError:
    RULE_SIZE = 79


class MockCreateSock:
    """Mock Sphinx response."""
    state = 0
    actions = (
        ('send', 65),               # recv 0x00|id[32]|alpha[32]
                                    # send beta[32]
        ('recv', b'\xaa\x16\xc7?\x81\xf1\xf9qw\x00\x0b\x1b\xdb\x0bA\xcf\x19'
         b'\xce\xeb_O\xe3\x99\xe5G\xb8M\xa9\x1a\xbcKM'),
        ('send', 32+RULE_SIZE+64),  # pubkey, rule, signature
        ('send', 32+64),            # id + signature
        ('recv', b"\x00\x00"),
        ('send', 0),                # pk[32], size[2], pkt[size], signature[64]
        ('recv', 'ok')
    )

    def send(self, pkt):
        action = self.actions[self.state]
        assert action[0] == 'send'  # nosec
        if action[1]:
            assert len(pkt) == action[1]  # nosec
        self.state += 1

    def recv(self, size):
        action = self.actions[self.state]
        assert action[0] == 'recv'  # nosec
        assert size == len(action[1])  # nosec
        self.state += 1
        return action[1]

    def close(self):
        return


def challenge(_):
    return (
        b"\xaeiOo\xda\x8d54#\x02\x03uBXr\xdfSie\xbb\xfb?_\x07Z\xb7b'\xd1n"
        b"\xde\x00",
        b'\xdc\xb2\x9c\xf6\x06\xa4\x82\x18\xc2\xc4$\xed\x01(\x12\x16\xeb@'
        b'\xdeOr\xca\x14\xf7\xf6\xb7\x04\x86B\xdaoW'
    )


def finish(w, x, y, z):
    return b'\\\xd6{\xed\xc70\xa1\xb3\xca\xeb\x0b\x91p\x11\x15\xe9P\xdfx\xe1'
    b'\x8f\x12\x96[\x05\xed\x8c\xad\xb8\xeb\xd7Z'


def connect():
    return MockCreateSock()


@tests.skipIfNoModule('pwdsphinx')
class TestExportSphinx(tests.Test):
    """Test sphinx general features."""

    @classmethod
    def setUpClass(cls):
        pwdsphinx.connect = connect
        pwdsphinx.sphinxlib.challenge = challenge
        pwdsphinx.sphinxlib.finish = finish

    def setUp(self):
        self.sphinx = Sphinx(self.prefix)

    def test_sphinx_exist(self):
        """Testing: exist."""
        self.assertTrue(self.sphinx.exist())

    def test_sphinx_isvalid(self):
        """Testing: isvalid."""
        self.assertTrue(self.sphinx.isvalid())


@tests.skipIfNoModule('pwdsphinx')
class TestExportSphinxInsert(tests.Test):
    """Test Sphinx insert features."""

    @classmethod
    def setUpClass(cls):
        pwdsphinx.connect = connect
        pwdsphinx.sphinxlib.challenge = challenge
        pwdsphinx.sphinxlib.finish = finish

    @patch("getpass.getpass")
    def test_sphinx_insert(self, pw):
        """Testing: sphinx insert."""
        pw.return_value = self.masterpassword
        entry = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }

        with Sphinx(self.prefix) as sphinx:
            sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_empty(self, pw):
        """Testing: sphinx insert empty."""
        pw.return_value = self.masterpassword
        entry = {'path': 'test'}

        with Sphinx(self.prefix) as sphinx:
            with self.assertRaises(PMError):
                sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_history(self, pw):
        """Testing: sphinx insert history."""
        pw.return_value = self.masterpassword
        entry = {'is_a_history_entry': True, 'path': 'test'}

        with Sphinx(self.prefix) as sphinx:
            with self.assertRaises(PMError):
                sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_no_login(self, pw):
        """Testing: sphinx insert no login."""
        pw.return_value = self.masterpassword
        entry = {'password': "dummy", 'path': 'test'}

        with Sphinx(self.prefix) as sphinx:
            with self.assertRaises(PMError):
                sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_path(self, pw):
        """Testing: sphinx insert path."""
        pw.return_value = self.masterpassword
        entry = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }

        with Sphinx(self.prefix) as sphinx:
            sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_weak(self, pw):
        """Testing: sphinx insert weak password."""
        pw.return_value = self.masterpassword
        entry = {
            'password': 'password',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }

        with Sphinx(self.prefix) as sphinx:
            sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_reused(self, pw):
        """Testing: sphinx insert password reused."""
        pw.return_value = self.masterpassword
        entries = [{
            'password': 'password',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }, {
            'password': 'password',
            'login': '44jle5q3fdvrprmaahozexy2pi',
            'url': 'https://twitter.com:443',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }]

        with Sphinx(self.prefix) as sphinx:
            for entry in entries:
                sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_too_long(self, pw):
        """Testing: sphinx insert too long."""
        pw.return_value = self.masterpassword
        entry = {
            'password': 'lnqYm3ZWtm44jle5q3fdvrprmaahozexy2pi44jle5q3fdvrprmaa'
                        'hozexy2pi44jle5q3fdvrprmaahozexy2pilnqYm3ZWtm44jle5q3'
                        'fdvrprmaahozexy2pi44jle5q3fdvrprmaahozexy2pi44jle5q3f'
                        'dvrprmaahozexy2pipassword',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }

        with Sphinx(self.prefix) as sphinx:
            with self.assertRaises(PMError):
                sphinx.insert(entry)
