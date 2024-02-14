# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
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
    keyslist = [
        'title', 'password', 'login', 'database', 'host', 'port', 'url',
        'email', 'phone', 'location', 'description', 'comments'
    ]
    keys = {
        'title': 'name',
        'password': 'generic-password',
        'login': 'generic-username',
        'database': 'generic-database',
        'host': 'generic-hostname',
        'hostdomain': 'generic-domain',
        'port': 'generic-port',
        'url': 'generic-url',
        'email': 'generic-email',
        'phone': 'phone-phonenumber',
        'location': 'generic-location',
        'description': 'description',
        'group': '',
        'comments': 'notes'
    }

    @classmethod
    def _getvalue(cls, element):
        key = element.tag
        if key == 'field':
            key = element.attrib.get('id', '')
        if key in ('generic-pin', 'generic-code'):
            key = 'generic-password'
        if key == 'updated':
            return key, ''
        return key, element.text

    def _import(self, element, path=''):
        for xmlentry in element.findall('entry'):
            if xmlentry.attrib.get('type', '') == 'folder':
                _path = os.path.join(path, xmlentry.find('name').text)
                self._import(xmlentry, _path)
            else:
                entry = self._getentry(xmlentry)
                entry['group'] = path

                host = entry.get('host', None)
                # Fix older Revelation storing Websites in Generic entries
                if host and 'url' not in entry:
                    for protocol in ['http://', 'https://']:
                        if host.startswith(protocol):
                            entry['url'] = entry.pop('host')
                            break
                domain = entry.pop('hostdomain', None)
                if domain:
                    if host:
                        if not host.endswith(domain):
                            entry['host'] = f'{host}.{domain}'
                    else:
                        entry['host'] = domain

                self.data.append(entry)


register_managers(Revelation)
