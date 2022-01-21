# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#

import csv
from typing import List

from pass_import.core import Cap, register_detecters
from pass_import.detecter import Formatter
from pass_import.errors import FormatError
from pass_import.manager import PasswordImporter


class CSV(Formatter, PasswordImporter):
    """Base class for CSV based importers.

    :param list fieldnames: The list of CSV field names
    :param str csv_header: If required special csv header to look for in the
        file.

    """
    cap = Cap.FORMAT | Cap.IMPORT
    format = 'csv'
    csv_header = ''
    fieldnames: List = []
    quotechar = '"'
    reader = None

    # Import method

    def parse(self):
        """Parse CSV based file."""
        fields = None if not self.fieldnames else self.fieldnames
        self.reader = csv.DictReader(self.file,
                                     fieldnames=fields,
                                     delimiter=self.delimiter,
                                     quotechar=self.quotechar)
        if not self.checkheader(self.header(), self.only):
            raise FormatError()

        keys = self.invkeys()
        for row in self.reader:
            entry = {}
            for col in row:
                entry[keys.get(col, col)] = row.get(col, None)

            self.data.append(entry)

    # Format recognition methods

    def is_format(self):
        """Return True if the file is a CSV file."""
        try:
            dialect = csv.Sniffer().sniff(self.file.read(4096),
                                          delimiters=self.delimiter)
            if dialect.quotechar != self.quotechar:  # pragma: no cover
                return False
            self.file.seek(0)
            self.reader = csv.DictReader(self.file, dialect=dialect)
        except (csv.Error, UnicodeDecodeError):
            return False
        return True

    def checkheader(self, header, only=False):
        """Ensure the file header is the same than the pm header."""
        try:
            if only and len(self.reader.fieldnames) != len(header):
                return False
            for csvkey in header:
                if csvkey not in self.reader.fieldnames:
                    return False
            return True
        except csv.Error:
            return False

    @classmethod
    def header(cls):
        """Header for CSV file."""
        return cls.keys.values()


register_detecters(CSV)
