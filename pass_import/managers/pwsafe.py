# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os

from pass_import.core import register_managers
from pass_import.formats.xml import XML


class Pwsafe(XML):
    """Importer for Pwsafe in XML format."""
    name = 'pwsafe'
    url = 'https://pwsafe.org'
    hexport = 'File > Export To > XML Format'
    himport = 'pass import pwsafe file.xml'
    xml_header = {'root': 'passwordsafe'}
    keyslist = [
        'title', 'password', 'login', 'url', 'email', 'comments', 'group'
    ]
    keys = {
        'title': 'title',
        'password': 'password',
        'login': 'username',
        'url': 'url',
        'email': 'email',
        'comments': 'notes',
        'group': 'group'
    }

    def _import(self, element, path=''):
        delimiter = element.attrib['delimiter']
        for xmlentry in element.findall('entry'):
            entry = self._getentry(xmlentry)
            entry['group'] = entry.get('group', '').replace('.', os.sep)
            entry['comments'] = entry.get('comments',
                                          '').replace(delimiter, '\n')
            histkey = './pwhistory/history_entries/history_entry'
            for historyentry in xmlentry.findall(histkey):
                for hist in historyentry:
                    xmlkey, value = self._getvalue(hist)
                    xmlkey += historyentry.attrib.get('num', '')
                    entry[xmlkey] = value
            self.data.append(entry)


register_managers(Pwsafe)
