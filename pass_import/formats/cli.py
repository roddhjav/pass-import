# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
#

import os
import shutil
from abc import abstractmethod
from subprocess import PIPE, Popen  # nosec

from pass_import.core import Cap
from pass_import.errors import PMError
from pass_import.manager import PasswordExporter, PasswordImporter


class CLI(PasswordImporter, PasswordExporter):
    """Base class for CLI based importer and exporter."""
    cap = Cap.IMPORT | Cap.EXPORT
    format = 'cli'
    command = ''

    def __init__(self, prefix=None, settings=None):
        self._binary = shutil.which(self.command)
        if self._binary is None:
            raise PMError(f"{self.command} is required.")  # pragma: no cover

        self.env = dict(**os.environ)
        super().__init__(prefix, settings)

    def _setenv(self, var, env=None, value=None):
        """Add var in the environment variables dictionary."""
        if env is None:
            env = var
        if env in os.environ:
            self.env[var] = os.environ[env]
        if value is not None:
            self.env[var] = value

    def _call(self, command, data=None, nline=True):
        """Call to a command."""
        if isinstance(data, bytes):
            nline = False
        with Popen(command, universal_newlines=nline, env=self.env, stdin=PIPE,
                   stdout=PIPE, stderr=PIPE, shell=False) as process:
            (stdout, stderr) = process.communicate(data)
            res = process.wait()
            return res, stdout, stderr

    def _command(self, arg, data=None, nline=True):
        """Call to the password manager cli command."""
        command = [self._binary]
        command.extend(arg)
        res, stdout, stderr = self._call(command, data, nline)
        if res:
            raise PMError(f"{stderr} {stdout}")
        return stdout

    def exist(self):
        """Nothing to do."""
        return True

    @abstractmethod
    def parse(self):
        """Parse the password manager repository and retrieve passwords."""

    @abstractmethod
    def insert(self, entry):
        """Insert a password entry into the password repository."""
