# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

from typing import List
from abc import abstractmethod

from pass_import.core import Asset, Cap


class Detecter(Asset):
    """Abstract Password manager format/encryption detection.

    To be listed as detecter a class must be registered using
    :func:`~register_detecters`

    """

    def detecter_open(self):
        """Detector context manager. Only required if different than open."""
        self.open()

    def detecter_close(self):
        """Detector context manager. Only required if different than close."""
        self.close()


class Decrypter(Detecter):
    """File encryption detection and decryption."""
    cap = Cap.DECRYPT

    @abstractmethod
    def decrypt(self):
        """Decrypt the data source.

        :return: Plain data

        """


class Formatter(Detecter):
    """Manager format dectection."""
    cap = Cap.FORMAT

    @abstractmethod
    def is_format(self) -> bool:
        """Return ``True`` if the prefix has same format than the pm."""

    @abstractmethod
    def checkheader(self, header: List, only: bool = False) -> bool:
        """Ensure the file header is the same than the pm header."""

    @classmethod
    @abstractmethod
    def header(cls):
        """Commom interface to get format header."""
