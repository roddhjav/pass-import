# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import json

from pass_import.core import Cap, register_detecters
from pass_import.detecter import Formatter
from pass_import.manager import PasswordImporter


class JSON(Formatter, PasswordImporter):
    """Base class for JSON based importers."""
    cap = Cap.FORMAT | Cap.IMPORT
    format = 'json'
    json_header = {}
    jsons = None

    # Import methods

    def parse(self):
        """Parse JSON based file."""
        raise NotImplementedError()

    # Format recognition methods

    def is_format(self) -> bool:
        """Return True if the file is a JSON file."""
        try:
            self.jsons = json.loads(self.file.read())
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            return False
        return True

    def _ensureheader(self, data, header) -> bool:
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

    def checkheader(self, header, only=False) -> bool:
        """Ensure the file header is the same than the pm header."""
        return self._ensureheader(self.jsons, header)

    @classmethod
    def header(cls):
        """Header for JSON file."""
        return cls.json_header


register_detecters(JSON)
