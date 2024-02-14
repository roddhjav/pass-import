# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from pass_import.core import register_managers
from pass_import.formats.xml import XML


class FigaroPM(XML):
    """Importer for Figaro Password Manager in XML format."""
    name = 'fpm'
    url = 'http://fpm.sourceforge.net'
    hexport = 'File > Export Passwords: Plain XML'
    himport = 'pass import fpm file.xml'
    xml_header = {'root': 'FPM'}
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'user',
        'url': 'url',
        'comments': 'notes',
        'group': 'category'
    }

    @classmethod
    def _getroot(cls, tree):
        return tree.find('PasswordList')

    def _import(self, element, path=''):
        for xmlentry in element.findall('PasswordItem'):
            entry = self._getentry(xmlentry)
            self.data.append(entry)


class Kedpm(FigaroPM):
    """Importer for Ked Password Manager in XML format."""
    name = 'kedpm'
    url = 'http://fpm.sourceforge.net'
    hexport = 'File > Export Passwords: Plain XML'
    himport = 'pass import kedpm file.xml'


register_managers(FigaroPM, Kedpm)
