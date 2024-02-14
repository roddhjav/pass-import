# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import re
from typing import Dict, List
from collections import defaultdict

# Cleaning variables.
SEPARATOR = '-'
NOTITLE = 'notitle'
PROTOCOLS = ['http://', 'https://']
INVALIDS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\0', '\t']
CLEANS = {
    ' ': '-',
    '&': 'and',
    '@': 'At',
    "'": '',
    '[': '',
    ']': '',
}


def cmdline(string: str, cleans: Dict[str, str] = None) -> str:
    """Make the string more command line friendly."""
    if not cleans:
        cleans = CLEANS

    return replaces(cleans, string)


def convert(string: str) -> str:
    """Convert invalid characters by the separator in a string."""
    characters = dict(zip(INVALIDS, [SEPARATOR] * len(INVALIDS)))
    return replaces(characters, string)


def domain(string: str) -> str:
    """Return the hostname part of a (potential) URLs."""
    for component in string.split('/'):
        if component != '':
            return component
    return string


def group(string: str) -> str:
    """Remove invalids characters in a group. Convert sep to os.sep."""
    characters = dict(zip(INVALIDS, [SEPARATOR] * len(INVALIDS)))
    characters['/'] = os.sep
    characters['\\'] = os.sep
    return replaces(characters, string)


def cpath(entry: Dict[str, str], path: str, cmdclean: bool, conv: bool) -> str:
    """Create path from title and group."""
    ptitle = ''
    for key in ['title', 'host', 'url', 'login']:
        if key in entry and entry[key]:
            ptitle = entry[key]
            if key in ['title', 'host', 'url']:
                ptitle = protocol(ptitle)
                if key in ['host', 'url']:
                    ptitle = domain(ptitle)

            ptitle = title(ptitle)
            if cmdclean:
                ptitle = cmdline(ptitle)
            if conv:
                ptitle = convert(ptitle)
            if ptitle != '':
                if os.path.basename(path) != ptitle:
                    path = os.path.join(path, ptitle)
                    break

    if ptitle == '' and os.path.basename(path) != NOTITLE:
        path = os.path.join(path, NOTITLE)
    entry.pop('title', '')
    return path


def dpaths(data: List[Dict[str, str]], cmdclean: bool, conv: bool):
    """Create subfolders for duplicated paths."""
    duplicated = defaultdict(list)
    for idx, entry in enumerate(data):
        path = entry.get('path', '')
        duplicated[path].append(idx)

    for path in duplicated:
        if len(duplicated[path]) > 1:
            for idx in duplicated[path]:
                entry = data[idx]
                entry['path'] = cpath(entry, path, cmdclean, conv)


def protocol(string: str) -> str:
    """Remove the protocol prefix in a string."""
    characters = dict(zip(PROTOCOLS, [''] * len(PROTOCOLS)))
    return replaces(characters, string)


def replaces(characters: Dict[str, str], string: str) -> str:
    """General purpose replace function."""
    for key in characters:
        string = string.replace(key, characters[key])
    return string


def title(string: str) -> str:
    """Clean the title from separator before addition to a path."""
    characters = {'/': SEPARATOR, '\\': SEPARATOR}
    return replaces(characters, string)


def unused(entry: Dict[str, str]) -> Dict[str, str]:
    """Remove unused keys and empty values."""
    empty = [k for k, v in entry.items() if not v]
    for key in empty:
        entry.pop(key)
    return entry


def duplicate(data: List[Dict[str, str]]):
    """Add number to the remaining duplicated path."""
    seen = set()
    for entry in data:
        idx_added = False
        path = entry.get('path', '')
        if path in seen:
            idx = 1
            while path in seen:
                if not idx_added:
                    path += SEPARATOR + str(idx)
                    idx_added = True
                else:
                    path = re.sub(rf'^(.*){SEPARATOR}{idx}$',
                                  rf'\1{SEPARATOR}{idx + 1}',
                                  path)
                    idx += 1
            seen.add(path)
            entry['path'] = path
        else:
            seen.add(path)


def otp(data: List[Dict[str, str]]):
    """Format the otpauth url with sane default."""
    for entry in data:
        if 'otpauth' in entry:
            if not entry['otpauth'].startswith('otpauth://'):
                secret = entry['otpauth']
                otp = f"otpauth://totp/{entry.get('title', 'otp-secret')}"
                otp += f"?secret={secret}"
                entry['otpauth'] = otp
