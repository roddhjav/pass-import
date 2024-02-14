# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.formats.xml import XML


class KeepassxXML(XML):
    """Importer for KeepassX in XML format."""
    name = 'keepassx'
    url = 'https://www.keepassx.org'
    hexport = 'File > Export to > Keepass XML File'
    himport = 'pass import keepassx file.xml'
    group = 'group'
    entry = 'entry'
    xml_header = {
        'doctype': '<!DOCTYPE KEEPASSX_DATABASE>',
        'root': 'database'
    }
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'comments': 'comment'
    }

    @classmethod
    def _getpath(cls, element, path=''):
        title = ''
        if element.tag != 'database':
            if element.find('title').text:
                title = element.find('title').text
        return os.path.join(path, title)

    def _import(self, element, path=''):
        path = self._getpath(element, path)
        for group in element.findall(self.group):
            self._import(group, path)
        for xmlentry in element.findall(self.entry):
            entry = self._getentry(xmlentry)
            entry['group'] = path
            self.data.append(entry)


register_managers(KeepassxXML)
