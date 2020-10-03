# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import json
import re

from pass_import.core import Cap, register_detecters
from pass_import.detecter import Formatter
from pass_import.manager import PasswordImporter


class JSON(Formatter, PasswordImporter):
    """Base class for JSON based importers."""
    cap = Cap.FORMAT | Cap.IMPORT
    format = 'json'
    json_header = dict()
    jsons = None

    # Import methods

    def parse(self):
        """Parse JSON based file."""
        raise NotImplementedError()

    # Format recognition methods

    def is_format(self):
        """Return True if the file is a JSON file."""
        try:
            self.jsons = json.loads(self.file.read())
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            return False
        return True

    def _ensureheader(self, data, header):
        """Ensure the data is in the header format.

        :return bool:
            True or False either the header match the json data.

        """
        # pylint: disable=too-many-return-statements
        if isinstance(header, type):
            if data is not None and not isinstance(data, header):
                return False
            return True

        if isinstance(data, list):
            if not isinstance(header, list):
                return False
            for item in data:
                if not self._ensureheader(item, header[0]):
                    return False
            return True

        if isinstance(data, dict):
            if not isinstance(header, dict):
                return False
            for key, value in header.items():
                if key not in data or not self._ensureheader(data[key], value):
                    return False
            return True

        return data == header

    def checkheader(self, header, only=False):
        """Ensure the file header is the same than the pm header."""
        return self._ensureheader(self.jsons, header)

    @classmethod
    def header(cls):
        """Header for JSON file."""
        return cls.json_header


class PIF(JSON):
    """Base class for PIF based importers.

    :param list ignore: List of key in the PIF file to not try to import.

    """
    format = '1pif'
    encoding = 'utf-8-sig'
    ignore = {'keyID', 'typeName', 'uuid', 'openContents', 'URLs'}

    # Import methods

    @staticmethod
    def pif2json(file):
        """Convert 1pif to json: https://github.com/eblin/1passpwnedcheck."""
        data = file.read()
        cleaned = re.sub(r'(?m)^\*\*\*.*\*\*\*\s+', '', data)
        cleaned = cleaned.split('\n')
        cleaned = ','.join(cleaned).rstrip(',')
        cleaned = '[%s]' % cleaned
        return json.loads(cleaned)

    def parse(self):
        """Parse PIF based file."""
        jsons = self.pif2json(self.file)
        keys = self.invkeys()
        folders = dict()
        for item in jsons:
            if item.get('typeName', '') == 'system.folder.Regular':
                key = item.get('uuid', '')
                folders[key] = {
                    'group': item.get('title', ''),
                    'parent': item.get('folderUuid', '')
                }

            elif item.get('typeName', '') == 'webforms.WebForm':
                entry = dict()
                scontent = item.pop('secureContents', {})
                fields = scontent.pop('fields', [])
                for field in fields:
                    name = field.get('name', '')
                    designation = field.get('designation', '')
                    jsonkey = name or designation
                    key = keys.get(jsonkey, jsonkey)
                    entry[key] = field.get('value', '')

                item.update(scontent)
                for key, value in item.items():
                    if key not in self.ignore:
                        entry[keys.get(key, key)] = value
                self.data.append(entry)
        self._sortgroup(folders)

    # Format recognition method

    def is_format(self):
        """Return True if the file is a 1PIF file."""
        try:
            self.jsons = self.pif2json(self.file)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            return False
        return True

    def checkheader(self, header, only=False):
        """No header check is needed."""
        return True


register_detecters(JSON, PIF)
