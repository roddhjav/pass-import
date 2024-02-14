# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.formats.csv import CSV
from pass_import.formats.kdbx import KDBX
from pass_import.formats.xml import XML


class Keepass(KDBX):
    """Importer/Exporter for Keepass encrypted KDBX format."""
    name = 'keepass'
    url = 'https://www.keepass.info'
    himport = 'pass import keepass file.kdbx'


class KeepassCSV(CSV):
    """Importer for Keepass in CSV format."""
    name = 'keepass'
    default = False
    url = 'https://www.keepass.info'
    hexport = 'File > Export > Keepass (CSV)'
    himport = 'pass import keepass file.csv'
    keys = {
        'title': 'Account',
        'password': 'Password',
        'login': 'Login Name',
        'url': 'Web Site',
        'comments': 'Comments'
    }


class KeepassXML(XML):
    """Importer for Keepass in XML format."""
    name = 'keepass'
    default = False
    url = 'https://www.keepass.info'
    hexport = 'File > Export > Keepass (XML)'
    himport = 'pass import keepass file.xml'
    xml_header = {'root': 'KeePassFile'}
    group = 'Group'
    entry = 'Entry'
    keys = {
        'title': 'Title',
        'password': 'Password',
        'login': 'UserName',
        'url': 'URL',
        'comments': 'Notes'
    }

    @classmethod
    def _getroot(cls, tree):
        root = tree.find('Root')
        return root.find('Group')

    @classmethod
    def _getpath(cls, element, path=''):
        """Generate path name from elements title and current path."""
        title = ''
        if element.tag == 'Group':
            title = element.find('Name').text
        if title is None:
            title = ''
        return os.path.join(path, title)

    @classmethod
    def _getvalue(cls, element):
        xmlkey = value = ''
        for child in element.findall('Key'):
            xmlkey = child.text
            value = element.find('Value').text
        return xmlkey, value

    def _import(self, element, path=''):
        path = self._getpath(element, path)
        for group in element.findall(self.group):
            self._import(group, path)
        for xmlentry in element.findall(self.entry):
            entry = self._getentry(xmlentry)
            entry['group'] = path
            self.data.append(entry)


register_managers(Keepass, KeepassCSV, KeepassXML)
