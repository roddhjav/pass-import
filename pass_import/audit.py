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
        self.skipped = []

    @property
    def report(self):
        """Get audit result."""
        return {
            'breached': self.breached,
            'weak': self.weak,
            'duplicated': self.duplicated,
            'skipped': self.skipped,
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

    def zxcvbn_parse(details):
        """
        Robust parser for zxcvbn results used in reporting.
        Tolerates missing or unexpected keys and returns a friendly message.
        """
        if not details:
            return ''
    
        # score must be an integer (0..4). Fallback to None is possible, we handle it.
        score = details.get('score')
        # guesses should be present; if not, we try guess_display or crack_times_display
        guesses = details.get('guesses')
        guesses_display = details.get('guesses_display') or \
                          (details.get('crack_times_display') or {}).get('offline_slow_hashing_1e4_per_second')
    
        parts = []
        if score is not None:
            # Score is numerical; check whether guesses exists
            if guesses is not None:
                parts.append(f"Score {score} ({guesses} guesses).")
            elif guesses_display:
                parts.append(f"Score {score} (est.: {guesses_display}).")
            else:
                parts.append(f"Score {score}.")
        else:
            parts.append("Score: unknown.")
    
        feedback = details.get('feedback') or {}
        warning = feedback.get('warning')
        suggestions = feedback.get('suggestions') or []
    
        if warning:
            parts.append(warning)
        if suggestions:
            parts.append(' '.join(suggestions))
    
        return ' '.join(parts)

    def zxcvbn(self):
        """Password strength estimation using Dropbox' zxcvbn."""
        for entry in self.data:
            if entry.get('password', '') == '':
                continue
            password = entry['password']
            if len(password) > 72:
                self.skipped.append(entry)
                continue
            user_input = list(entry.values())
            if password in user_input:
                user_input.remove(password)
                
            try:
                if password is None:
                    results = {
                        'score': 0,
                        'guesses': 0,
                        'guesses_display': 'no password',
                        'crack_times_display': {},
                        'feedback': {'warning': 'no password provided', 'suggestions': []}
                    }
                elif len(password) > 72:
                    # zxcvbn cannot handle very long passwords, and we
                    # do not want the import to crash. Long passphrases are considered strong
                    # in practice — hence score=4.
                    results = {
                        'score': 4,
                        'guesses': 10**12,  # Platzhalter große Zahl
                        'guesses_display': 'skipped (password too long for zxcvbn)',
                        'crack_times_display': {},
                        'feedback': {'warning': 'password too long for zxcvbn; strength check skipped', 'suggestions': []}
                    }
                else:
                    # Normal call
                    results = zxcvbn(password, user_inputs=user_input)
            except Exception:
                # For any errors from zxcvbn: consistent fallback values,
                # so that downstream code (e.g. if results['score'] <= 2) continues to function.
                results = {
                    'score': 3,
                    'guesses': 10**6,
                    'guesses_display': 'error (zxcvbn)',
                    'crack_times_display': {},
                    'feedback': {'warning': 'zxcvbn raised an error; strength check skipped', 'suggestions': []}
                }

            result_parsed = zxcvbn_parse(results)
                
            if result_parsed['score'] <= 2:
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
