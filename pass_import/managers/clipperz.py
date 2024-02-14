# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json

try:
    from defusedxml import ElementTree
except ImportError:
    from xml.etree import ElementTree

from pass_import.core import register_managers
from pass_import.errors import FormatError
from pass_import.formats.xml import HTML


class ClipperzHTML(HTML):
    """Importer for Clipperz in HTML+JSON format."""
    name = 'clipperz'
    url = 'https://clipperz.is'
    hexport = 'Settings > Data > Export: HTML + JSON'
    himport = 'pass import clipperz file.html'
    html_header = 'body/div/div/textarea'
    keys = {'login': 'username'}

    def parse(self):
        """Parse Clipperz HTML+JSON file."""
        # Extract the json from the html file.
        tree = ElementTree.XML(self.file.read())
        found = tree.find(self.html_header)
        if found is None:
            raise FormatError()

        # Parse JSON data
        keys = self.invkeys()
        for item in json.loads(found.text):
            entry = {}
            label = item.get('label', ' \ue009').split(' \ue009')
            entry['title'] = label[0]
            if len(label) > 1:
                entry['group'] = label[1]

            fields = item.get('currentVersion', {}).get('fields', {})
            for uid in fields:
                label = fields[uid].get('label', '')
                entry[keys.get(label, label)] = fields[uid].get('value', '')

            entry['comments'] = item.get('data', {}).get('notes', '')
            self.data.append(entry)


register_managers(ClipperzHTML)
