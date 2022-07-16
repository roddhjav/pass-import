# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2022 Stefan Marsiske <sphinx@ctrlc.hu>.
#
from pass_import.core import register_managers
from pass_import.formats.sphinx import SPHINX


class Sphinx(SPHINX):
    """Exporter for Sphinx."""
    name = 'sphinx'
    default = True
    url = 'https://github.com/stef/pwdsphinx/'

    def exist(self):
        """Nothing to do."""
        return True

register_managers(Sphinx)
