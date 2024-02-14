# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import yaml

from pass_import.core import Cap, register_detecters
from pass_import.detecter import Formatter
from pass_import.errors import FormatError
from pass_import.manager import PasswordImporter


class YAML(Formatter, PasswordImporter):
    """Base class for YAML based importers.

    :param dict yml_format: Dictionary that need to be present in the imported
        file to ensure the format is recognized.
    :param str rootkey: Root key where to find the data to import in the YAML.

    """
    cap = Cap.FORMAT | Cap.IMPORT
    format = 'yaml'
    yml_format = {}
    yamls = None
    rootkey = ''

    # Import method

    def parse(self):
        """Parse YAML based file."""
        self.yamls = yaml.safe_load(self.file)
        if not self.checkheader(self.header()):
            raise FormatError()

        keys = self.invkeys()
        for block in self.yamls[self.rootkey]:
            entry = {}
            for key, value in block.items():
                if value:
                    entry[keys.get(key, key)] = value
            self.data.append(entry)

    # Format recognition methods

    def is_format(self):
        """Return True if the file is a YAML file."""
        try:
            self.yamls = yaml.safe_load(self.file)
            if isinstance(self.yamls, str):
                return False
        except (yaml.scanner.ScannerError, yaml.parser.ParserError,
                UnicodeDecodeError):
            return False
        return True

    def checkheader(self, header, only=False):
        """Ensure the file header is the same than the pm header."""
        for key, value in header.items():
            if self.yamls.get(key, '') != value:
                return False
        return True

    @classmethod
    def header(cls):
        """Header for YML file."""
        return cls.yml_format


register_detecters(YAML)
