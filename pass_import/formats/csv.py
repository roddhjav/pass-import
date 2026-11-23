# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import csv

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
    fieldnames: list = []
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

    def is_format(self) -> bool:
        """Return True if the file is a CSV file."""
        try:
            dialect = csv.Sniffer().sniff(self.file.read(4096),
                                          delimiters=self.delimiter)
            if dialect.quotechar != self.quotechar:  # pragma: no cover
                return False
            self.file.seek(0)
            self.reader = csv.DictReader(self.file, dialect=dialect)

            # Context:
            #   1password can export data in:
            #   - 1PIF (json like format)
            #   - CSV
            # Problem:
            #   CSV sniffer considers the following line as a CSV
            #   line and will provide a dialect for it.
            #
            #   line: {"field0":"foo", ..., fieldX:"baz"}
            #
            #   This is clearly a JSON formatted line.
            # Solution:
            #    If the line looks like a JSON, then consider the
            #    file not a CSV file
            keys = [k for k in self.reader.fieldnames or [] if k]
            if (keys and keys[0].startswith('{') and keys[-1].endswith('}')
                    and all(':' in key for key in keys)):
                return False
        except (csv.Error, UnicodeDecodeError):
            return False
        return True

    def checkheader(self, header: list, only: bool = False) -> bool:
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
