# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import re
from collections import defaultdict

# Cleaning variables.
SEPARATOR = '-'
PROTOCOLS = ['http://', 'https://']
INVALIDS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\0']
CLEANS = {
    " ": '-',
    "&": "and",
    "@": "At",
    "'": "",
    "[": "",
    "]": "",
    "\t": ''
}


def cmdline(string, cleans=None):
    """Make the string more command line friendly."""
    if not cleans:
        cleans = CLEANS

    return replaces(cleans, string)


def convert(string):
    """Convert invalid caracters by the separator in a string."""
    caracters = dict(zip(INVALIDS, [SEPARATOR] * len(INVALIDS)))
    return replaces(caracters, string)


def group(string):
    """Remove invalids caracters in a group. Convert sep to os.sep."""
    caracters = dict(zip(INVALIDS, [SEPARATOR] * len(INVALIDS)))
    caracters['/'] = os.sep
    caracters['\\'] = os.sep
    return replaces(caracters, string)


def cpath(entry, path, cmdclean, conv):
    """Create path from title and group."""
    ptitle = ''
    for key in ['title', 'login', 'url']:
        if key in entry:
            ptitle = protocol(entry[key])
            ptitle = title(ptitle)
            if cmdclean:
                ptitle = cmdline(ptitle)
            if conv:
                ptitle = convert(ptitle)
            path = os.path.join(path, ptitle)
            break

    if ptitle == '':
        path = os.path.join(path, 'notitle')
    entry.pop('title', '')
    return path


def dpaths(data, cmdclean, conv):
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


def protocol(string):
    """Remove the protocol prefix in a string."""
    caracters = dict(zip(PROTOCOLS, [''] * len(PROTOCOLS)))
    return replaces(caracters, string)


def replaces(caracters, string):
    """General purpose replace function."""
    for key in caracters:
        string = string.replace(key, caracters[key])  # re.sub ?
    return string


def title(string):
    """Clean the title from separator before addition to a path."""
    caracters = {'/': SEPARATOR, '\\': SEPARATOR}
    return replaces(caracters, string)


def unused(entry):
    """Remove unused keys and empty values."""
    empty = [k for k, v in entry.items() if not v]
    for key in empty:
        entry.pop(key)
    return entry


def duplicate(data):
    """Add number to the remaining duplicated path."""
    seen = set()
    for entry in data:
        path = entry.get('path', '')
        if path in seen:
            idx = 1
            while path in seen:
                if re.search(r'%s(\d+)$' % SEPARATOR, path) is None:
                    path += SEPARATOR + str(idx)
                else:
                    path = path.replace(SEPARATOR + str(idx),
                                        SEPARATOR + str(idx + 1))
                    idx += 1
            seen.add(path)
            entry['path'] = path
        else:
            seen.add(path)
