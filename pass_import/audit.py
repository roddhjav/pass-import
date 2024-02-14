# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import hashlib

import requests
from zxcvbn import zxcvbn
from typing import List, Tuple

import pass_import


class PwnedAPI():
    """Simple wrapper for https://haveibeenpwned.com API."""

    def __init__(self):
        self.headers = {
            'user-agent': f"{pass_import.__title__}/{pass_import.__version__}"}

    def password_range(self, prefix: str) -> Tuple[List[str], List[int]]:
        """Query the haveibeenpwned api to retrieve the bucket ``prefix``."""
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        res = requests.get(url, headers=self.headers, verify=True, timeout=5)
        res.raise_for_status()

        hashes = []
        counts = []
        for item in res.text.split('\r\n'):
            partialhash, count = item.split(':')
            hashes.append(prefix + partialhash)
            counts.append(int(count))
        return (hashes, counts)


class Audit():
    """Audit passwords for vulnerabilities.

    Based on the PassAudit class from pass-audit.
    See https://github.com/roddhjav/pass-audit for more information.

    :param list[dict] data: The list of password entries to audit
        Each password entry is a dictionary.

    """

    def __init__(self, data):
        self.data = data
        self.breached = []
        self.weak = []
        self.duplicated = []

    @property
    def report(self):
        """Get audit result."""
        return {
            'breached': self.breached,
            'weak': self.weak,
            'duplicated': self.duplicated
        }

    def password(self):
        """K-anonimity password breach detection on haveibeenpwned.com."""
        # Generate the list of hashes and prefixes to query.
        data = []
        api = PwnedAPI()
        buckets = {}
        for entry in self.data:
            if entry.get('password', '') == '':
                continue
            password = entry['password'].encode("utf8")
            phash = hashlib.sha1(password).hexdigest().upper()  # nosec
            prefix = phash[0:5]
            data.append((entry, phash, prefix))
            if prefix not in buckets:
                buckets[prefix] = api.password_range(prefix)

        # Compare the data and return the breached passwords.
        for entry, phash, prefix in data:
            if phash in buckets[prefix][0]:
                index = buckets[prefix][0].index(phash)
                count = buckets[prefix][1][index]
                self.breached.append((entry.get('password', ''), count))

    def zxcvbn(self):
        """Password strength estimaton usuing Dropbox' zxcvbn."""
        for entry in self.data:
            if entry.get('password', '') == '':
                continue
            password = entry['password']
            user_input = list(entry.values())
            if password in user_input:
                user_input.remove(password)
            results = zxcvbn(password, user_inputs=user_input)
            if results['score'] <= 2:
                self.weak.append((password, results))

    def duplicates(self):
        """Check for duplicated passwords."""
        seen = {}
        for entry in self.data:
            if entry.get('password', '') == '':
                continue
            password = entry['password']
            if password in seen:
                seen[password].append(entry)
            else:
                seen[password] = [entry]

        for entries in seen.values():
            if len(entries) > 1:
                self.duplicated.append(entries)
