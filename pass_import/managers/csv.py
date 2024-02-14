# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import csv
import os

from pass_import.core import Cap, register_managers
from pass_import.errors import FormatError, PMError
from pass_import.formats.csv import CSV
from pass_import.manager import PasswordExporter


class GenericCSV(CSV, PasswordExporter):
    """Importer & Exporter in generic CSV format.

    :usage:
    You should use the --cols option to map columns to credential attributes.
    The recognized column names by pass-import are the following:
        'title', 'password', 'login', 'email', 'url', 'comments',
        'otpauth', 'group'
    ``title`` and ``group`` field are used to generate the password
    path. If you have otp data, they should be named as ``otpauth``.
    These are the *standard* field names. You can add any other field
    you want.

    """
    cap = Cap.IMPORT | Cap.EXPORT
    name = 'csv'
    himport = "pass import csv file.csv --cols 'url,login,,password'"
    writer = None

    # Import method

    def parse(self):
        """Parse Generic CSV file."""
        self.file.readline()
        if ',' in self.cols:
            self.fieldnames = self.cols.split(',')
        else:
            raise FormatError("no columns to map to credential attributes.")
        super().parse()

    # Export methods

    def exist(self):
        """Nothing to do."""
        return True

    def clean(self, cmdclean, convert):
        """Clean data for export in CSV a file."""
        super().clean(cmdclean, convert)
        fieldnames = set()
        for entry in self.data:
            path = entry.pop('path', '')
            entry['group'] = os.path.join(self.root, os.path.dirname(path))
            entry['title'] = os.path.basename(path)
            fieldnames.update(set(entry.keys()))

        if not self.all:
            fieldnames = self.keyslist
        for entry in self.data:
            for key in fieldnames:
                if key not in entry:
                    entry[key] = ''
        self.writer = csv.DictWriter(self.file,
                                     fieldnames=sorted(fieldnames),
                                     restval='',
                                     extrasaction='raise')
        self.writer.writeheader()

    def insert(self, entry):
        """Insert a password entry into a CSV file.

        :param dict entry: The password entry to insert.

        If ``all`` is true, all the entry values are printed.
        Otherwise, only the key present in ``keyslist`` are
        printed following the order from this list. The title, path, and group
        keys are ignored.

        Binary attachment is not supported.

        """
        if self.all:
            self.writer.writerow(entry)
        else:
            res = {}
            for key in self.keyslist:
                res[key] = entry.get(key, '')
            self.writer.writerow(res)

    # Context manager method

    def open(self):
        """Create/Re-create CSV exported file."""
        if self.action is Cap.IMPORT:
            super().open()
        else:
            if os.path.isfile(self.prefix):
                if self.force:
                    self.file = open(self.prefix, 'w', encoding=self.encoding)
                else:
                    raise PMError(f"{self.prefix} is already a file.")
            else:
                self.file = open(self.prefix, 'w', encoding=self.encoding)


register_managers(GenericCSV)
