# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.formats.xml import XML


class Revelation(XML):
    """Importer for Revelation in XML format."""
    name = 'revelation'
    url = 'https://revelation.olasagasti.info'
    hexport = 'File > Export: XML'
    himport = 'pass import revelation file.xml'
    xml_header = {'root': 'revelationdata'}
    keys = {
        'title': 'name',
        'password': 'generic-password',
        'login': 'generic-username',
        'url': 'generic-hostname',
        'comments': 'notes',
        'group': '',
        'description': 'description'
    }

    @classmethod
    def _getvalue(cls, element):
        key = element.tag
        if key == 'field':
            key = element.attrib.get('id', '')
        return key, element.text

    def _import(self, element, path=''):
        for xmlentry in element.findall('entry'):
            if xmlentry.attrib.get('type', '') == 'folder':
                _path = os.path.join(path, xmlentry.find('name').text)
                self._import(xmlentry, _path)
            else:
                entry = self._getentry(xmlentry)
                entry['group'] = path
                self.data.append(entry)


register_managers(Revelation)
