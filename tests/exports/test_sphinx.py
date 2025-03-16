# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 20220 Stefan Marsiske <sphinx@ctrlc.hu>.
#

from unittest.mock import patch
from tempfile import mkdtemp
from os import listdir, makedirs, path
from shutil import rmtree
import subprocess, time, pysodium

import tests
from pass_import.errors import PMError
from pass_import.managers.sphinx import Sphinx, PWDSPHINX
if PWDSPHINX:
    from pass_import.managers.sphinx import sphinx as pwdsphinx
import logging
logger = logging.getLogger(__name__)

servers = {'zero': {'host': 'localhost', 'port': 10000, 'ssl_cert': 'cert.pem'},
           'one':  {'host': 'localhost', 'port': 10001, 'ssl_cert': 'cert.pem'},
           'two':  {'host': 'localhost', 'port': 10002, 'ssl_cert': 'cert.pem'}}

cert_pem = """
-----BEGIN CERTIFICATE-----
MIIBhTCCASugAwIBAgIURt1h20rXWGwyV5nuLDp2NBaXsgkwCgYIKoZIzj0EAwIw
GDEWMBQGA1UEAwwNc3BoaW54IG9yYWNsZTAeFw0yMDA5MjkyMTI5MDBaFw0yMTA5
MjQyMTI5MDBaMBgxFjAUBgNVBAMMDXNwaGlueCBvcmFjbGUwWTATBgcqhkjOPQIB
BggqhkjOPQMBBwNCAATPl01K0Nuxm4wZaYzS4AvaXy4pIG96Zk5XC1o0TmkdnNPb
kgSUm6dx1OVvx3u8kVGRHYfgC7C4I414W2v41Hb4o1MwUTAdBgNVHQ4EFgQUtpha
TRgMR7SeM7gYPKoq8L874tcwHwYDVR0jBBgwFoAUtphaTRgMR7SeM7gYPKoq8L87
4tcwDwYDVR0TAQH/BAUwAwEB/zAKBggqhkjOPQQDAgNIADBFAiEAnN1Y9WDfVW6f
slgOnPs8eQdyoqA7S/rFf9wE/ZxR4tECICfCYMKpIRMYPEk2C+kqoJueB/JVdGKh
pYxdMvjx8bsj
-----END CERTIFICATE-----
"""

key_pem = """
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIBvDA1MfRSB+jbflO/Db0XkbHWoxHceapqqwdww/nXiHoAoGCCqGSM49
AwEHoUQDQgAEz5dNStDbsZuMGWmM0uAL2l8uKSBvemZOVwtaNE5pHZzT25IElJun
cdTlb8d7vJFRkR2H4AuwuCONeFtr+NR2+A==
-----END EC PRIVATE KEY-----
"""

@tests.skipIfNoModule('pwdsphinx')
class TestExportSphinx(tests.Test):
    """Test sphinx general features."""
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
        pwdsphinx.threshold=2
        pwdsphinx.verbose=True
        pwdsphinx.datadir = '/tmp/sphinx/'
        pwdsphinx.timeout = 30
        pwdsphinx.rwd_keys = True
        pwdsphinx.threshold = 2
        pwdsphinx.validate_password = False

        cls._root = mkdtemp(prefix='sphinx-oracle-root.')
        root = cls._root
        pks = []
        for idx, k in enumerate(servers.keys()):
            makedirs(f"{root}/servers/{idx}")
            with open(f"{root}/servers/{idx}/cert.pem", 'w') as fd:
                fd.write(cert_pem)
            with open(f"{root}/servers/{idx}/key.pem", 'w') as fd:
                 fd.write(key_pem)
            pk, sk = pysodium.crypto_sign_keypair()
            with open(f"{root}/servers/{idx}/ltsig.key", 'wb') as fd:
                fd.write(sk)
            servers[k]['ltsigkey']=pk
            servers[k]['ssl_cert']=f"{root}/servers/{idx}/cert.pem"
            with open(f"{root}/servers/{idx}/sphinx.cfg", 'w') as fd:
                fd.write(f'[server]\n'
                         f'verbose = true\n'
                         f'address = "127.0.0.1"\n'
                         f'port={10000+idx}\n'
                         f'timeout = 30\n'
                         f'max_kids = 5\n'
                         f'ssl_key= "key.pem"\n'
                         f'ssl_cert= "cert.pem"\n'
                         f'ltsigkey = "ltsig.key"\n'
                         f'datadir = "data"\n'
                         f'rl_decay=1800\n'
                         f'rl_threshold=10\n')
        cls._oracles = []
        for idx in range(len(servers)):
          log = open(f"{root}/servers/{idx}/log", "w")
          cls._oracles.append(
            (subprocess.Popen(["python3", path.dirname(path.abspath(pwdsphinx.__file__)) + "/oracle.py"], cwd = f"{root}/servers/{idx}/", stdout=log, stderr=log, pass_fds=[log.fileno()]), log))
          log.close()
        time.sleep(0.8)
        pwdsphinx.servers = servers
        pwdsphinx.create_masterkey()

    @classmethod
    def tearDownClass(cls):
        for p, log in cls._oracles:
            p.kill()
            r = p.wait()
            log.close()
        rmtree(cls._root)
        time.sleep(0.4)

    def tearDown(self):
      for idx in range(len(servers)):
          ddir = f"{self._root}/servers/{idx}/data/"
          if not path.exists(ddir): continue
          for f in listdir(ddir):
              if f == 'key': continue
              rmtree(ddir+f)

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
