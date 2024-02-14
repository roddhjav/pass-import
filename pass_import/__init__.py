# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#
"""Passwords importer swiss army knife."""

from collections import OrderedDict, defaultdict
from typing import Callable, List, Dict, Union, Generator

import pass_import.decrypters  # noqa
import pass_import.formats  # noqa
import pass_import.managers  # noqa
from pass_import.__about__ import (__author__, __copyright__, __email__,
                                   __license__, __summary__, __title__,
                                   __uri__, __version__)
from pass_import.core import Cap, get_detecters, get_managers

__all__ = [
    '__title__', '__summary__', '__uri__', '__version__', '__author__',
    '__email__', '__license__', '__copyright__'
]


class ManagerError(Exception):
    """Errors related to managers' management. Most likely a bug if raised."""


class Managers(set):
    """Provide an interface to manage the managers' classes easily."""

    def __init__(self):
        super().__init__(get_managers())

    def classes(self, cap=Cap.IMPORT, frmt=None) -> Generator:
        """Generate the classes of pm with capabilities and format."""
        ignore = {'csv'}
        for pm in self:
            if cap in pm.cap:
                if frmt:
                    if pm.name in ignore:
                        continue
                    if pm.format == frmt:
                        yield pm
                else:
                    yield pm

    def get(self, name, frmt='', version='', cap=Cap.IMPORT
            ) -> Union[Callable, None]:
        """Return a manager class from its classname or its format."""
        default = None
        for pm in self.classes(cap):
            # If name is a classname, return the class
            if pm.__name__ == name:
                return pm

            # If name is a password manager name, check its metadata
            if pm.name == name:
                if not default:
                    default = pm
                if pm.format == frmt and pm.version == version:
                    return pm

        if default:
            return default
        raise ManagerError(f'Unknown password manager: {name}')

    def clsnames(self, cap=Cap.IMPORT) -> List[str]:
        """Return the sorted list of password managers classes name."""
        names = set()
        for pm in self.classes(cap):
            names.add(pm.__name__)
        return sorted(names)

    def names(self, cap=Cap.IMPORT) -> List[str]:
        """Return the sorted list of password managers name."""
        names = set()
        for pm in self.classes(cap):
            names.add(pm.name)
        return sorted(names)

    def matrix(self, cap=Cap.IMPORT) -> Dict[str, List[Callable]]:
        """Return a dict of ordered managers classes and formats.

        :return dict matrix:
            { name: [pm_1, pm_2, ..., pm_n] } such as pm1 is the dedault pm and
            the other pm are ordered by they format.
        """
        umatrix = defaultdict(list)  # unordered  matrix
        for pm in self.classes(cap):
            umatrix[pm.name].append(pm)

        matrix = defaultdict(list)
        for name in umatrix:
            formats = []
            default = None
            for pm in umatrix[name]:
                if pm.default:
                    default = pm
                else:
                    formats.append(pm)

            formats.sort(key=lambda x: x.format)
            formats.insert(0, default)
            matrix[name] = formats
        return matrix


class Detecters(OrderedDict):
    """An ordered dictionary of the password managers format supported.

    This format dictionary is ordered to take care of the following
    requirements:

    - Most common format first
    - Parent format first. Eg: ``XML`` before ``HTML``,
      ``JSON`` before ``YAML``...

    """
    orders = {
        Cap.FORMAT: [
            'csv', 'xml', 'json', 'kdbx', 'yaml', '1pif', 'html', 'keychain'
        ],
        Cap.DECRYPT: []
    }

    def __init__(self, cap=Cap.FORMAT):
        self.cap = cap
        if self.cap not in Cap.FORMAT | Cap.DECRYPT:
            raise ManagerError('Capability not supported')

        cls = get_detecters()
        detecters = OrderedDict()
        for frmt in self.orders[cap]:
            for pm in cls:
                if pm.format == frmt and cap in pm.cap:
                    detecters[pm.format] = pm

        for pm in cls:
            if pm.format not in self.orders[cap] and cap in pm.cap:
                detecters[pm.format] = pm
        super().__init__(detecters)
