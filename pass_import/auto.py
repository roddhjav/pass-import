# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import io
import os
from contextlib import contextmanager
from typing import Callable, List, Tuple, Union

import pass_import
from pass_import.core import Cap
from pass_import.detecter import Formatter
from pass_import.errors import PMError


class DummyDetecter(Formatter):
    """Dummy detecter class.

    In the detector context manager, if the :func:`~detecter_open` method of a
    Detecter object fails, it means the format tested is not the format
    considered. Then, we fall back to this dummy password manager class to fail
    silently and continue the search of the file password manager and format.

    """

    def detecter_open(self):
        """Do nothing."""

    def detecter_close(self):
        """Do nothing."""

    def is_format(self) -> bool:
        """Return ``False``."""
        return False

    def checkheader(self, header, only=False) -> bool:
        """No header check."""
        return False  # pragma: no cover

    @classmethod
    def header(cls) -> str:
        """No header."""
        return ''  # pragma: no cover


@contextmanager
def detector(cls, prefix, settings=None):
    """Context manager for password format/encryption detection."""
    manager = cls(prefix, settings)
    try:
        manager.detecter_open()
    except (PMError, IsADirectoryError):
        dummy = DummyDetecter(prefix)
        dummy.detecter_open()
        yield dummy
        dummy.detecter_close()
    else:
        yield manager
        manager.detecter_close()


class AutoDetect():
    """Give a file, detect the format, and the password manager.

    Considering a manager's name and optional version number, tell if a given
    path is supported by the password manager and, if yes, tell what format is
    supported.

    :param str name: (optional) Name of the password manager. Only the
        ``manager`` method can be used without the manager name.
    :param str version: (optional) Version number of the password manager.

    """

    def __init__(self, name='', settings=None):
        self.settings = {} if settings is None else settings
        self.managers = pass_import.Managers()
        self.formats = pass_import.Detecters(Cap.FORMAT)
        self.decrypters = pass_import.Detecters(Cap.DECRYPT)
        self.classes = self.managers.matrix().get(name, [])
        self.stream = self.settings.get('decrypted', False)

    def default(self, name='') -> Callable:
        """Retrieve the class of the default importer."""
        classes = self.classes
        if name != '':
            classes = self.managers.matrix().get(name, [])
        for pm in classes:
            if pm.default:
                return pm
        raise pass_import.ManagerError('No default manager found.')

    def format(self, path: str) -> Callable:
        """Full format detection of a file for a given password manager.

        - If only one format supported, use it.
        - If path is a file, try to open it with all supported format.
        - Then if the format is not supported by :func:`~tryopen`,
          open it if this is the last remaining.
        - Get the default format otherwise

        :param str path: Path, directory, or plain data of the manager.
        :returns PasswordManager: The detected password manager class.
            ``None`` if not found.

        """
        if len(self.classes) == 1:
            return self.classes[0]

        if not (self.stream or os.path.isfile(path) or os.path.isdir(path)):
            return self.default()

        pm, unknowns = self._tryopen(path)
        if pm:
            return pm
        if len(unknowns) == 1:
            return unknowns[0]
        return self.default()  # pragma: no cover

    def manager(self, path: str) -> Union[Callable, None]:
        """Full format detection of a file without knowing the  manager's name.

        :algorithm:

        .. code-block:: console

            For all format classes in Formats:
                Open the path,
                Check if it is in the considered format,
                If yes:
                    For all managers that support the format:
                        Compare manager header for the file header.

        :param str path: Path, directory, or plain data of the manager.
        :returns PasswordManager: The detected password manager class.
            ``None`` if not found.

        """
        if not (self.stream or os.path.isfile(path) or os.path.isdir(path)):
            return None

        prefix = path
        for frmt in self.formats:
            if self.stream:
                prefix = io.StringIO(path)
            with detector(self.formats[frmt], prefix, self.settings) as file:
                if file.is_format():
                    for pm in self.managers.classes(frmt=frmt):
                        if file.checkheader(pm.header(), pm.only):
                            return pm
        return None

    def _tryopen(self, path: str
                 ) -> Tuple[Union[Callable, None], List[Callable]]:
        """Knowing the manager's name, try to open the path in all formats.

        :algorithm:

        .. code-block:: console

            For all classes that support the password manager 'name':
                If the format is supported by pass-import:
                    Open the path
                    Check if it is in the considered format
                        Compare manager header against the file header
                Else:
                    The could format could be this one, update unknowns list.

        :param str path: Path, directory, or plain data of the manager.
        :returns PasswordManager: The detected password manager class.
            ``None`` if not found.
        :returns list: List of untested :term:`pm`, format could be any of
            them.

        """
        unknowns = []
        prefix = path
        for pm in self.classes:
            if pm.format in self.formats:
                if self.stream:
                    prefix = io.StringIO(path)
                with detector(pm, prefix, self.settings) as file:
                    if file.is_format():
                        if file.checkheader(file.header(), file.only):
                            return pm, []
            else:
                unknowns.append(pm)
        return None, unknowns
