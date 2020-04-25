#!/usr/bin/env python3
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2020 Alexandre PUJOL <alexandre@pujol.io>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# This script updates the readme file in this repo.

import io

import pass_import
from pass_import.core import Cap
from pass_import.__main__ import ArgParser

MANAGERS = pass_import.Managers()


# Internal tools
# ---------------

def replace(marker_begin, marker_end, string, newcontent):
    """Replace data inside string markers."""
    begin = string.find(marker_begin)
    end = string.find(marker_end)
    return string.replace(string[begin + len(marker_begin):end], newcontent)


class ManagerMeta():
    """Generate currated password managers metadata."""
    guide = 'this guide: '

    def __init__(self, pm, ext=True, md=True):
        self.pm = pm
        self.md = md
        self.prog = 'pass import' if ext else 'pimport'

    def urlto_markdown(self, string):
        """Markdonize link."""
        if self.guide in string:
            msg = string.split(self.guide)
            url = msg.pop()
            string = ''.join(msg) + '[this guide](%s)' % url
        return string

    def urlto_man(self, string):
        """Remove markdown link from a string."""
        if self.guide in string:
            string = string.replace(self.guide, 'this guide: \\fI')
            string += '\\fP'
        return string

    @property
    def format(self):
        """Get format formated."""
        res = ''
        if self.pm.format != '':
            if self.md:
                res = self.pm.format
            else:
                res = '(%s)' % self.pm.format
        return res

    @property
    def version(self):
        """Get version formated."""
        res = ''
        if self.pm.version != '':
            res = ' v%s' % self.pm.version
        return res

    @property
    def url(self):
        """Get url formated."""
        return self.pm.url

    @property
    def hexport(self):
        """Get export help formated."""
        if self.md:
            res = self.urlto_markdown(self.pm.hexport)
        else:
            res = self.urlto_man(self.pm.hexport)
        if res == '':
            res = 'Nothing to do'
        return res

    @property
    def himport(self):
        """Get import help formated."""
        res = self.pm.himport
        if res == '':
            res = '%s %s file.%s' % (self.prog, self.pm.name, self.pm.format)
        return res

    @property
    def usage(self):
        """Get usage formated."""
        res = self.pm.usage()
        if res != '':
            res = '%s\n\n' % res
        return res

    @property
    def description(self):
        """Get description formated."""
        return self.pm.description()


# Generator functions
# --------------------

# README.md

def table_importer():
    """Generate the new importer table."""
    res = (
        '| **Password Manager** | **Formats** | **How to export Data** | **Command line** |\n'  # noqa
        '|:--------------------:|:-----------:|:----------------------:|:----------------:|\n'  # noqa
    )

    matrix = MANAGERS.matrix()
    for name in sorted(matrix):
        formats = []
        hexports = []
        himports = []
        for pm in matrix[name]:
            mm = ManagerMeta(pm, md=True)
            formats.append('`%s%s`' % (mm.format, mm.version))
            if len(hexports) == 0 or hexports[0] != mm.hexport:
                hexports.append(mm.hexport)
            himports.append(mm.himport)
        frmt = ', '.join(formats)
        hexport = '* **OR** *'.join(hexports)
        himport = '` **OR** `'.join(himports)

        res += "| [%s](%s) | %s | *%s* | `%s` |\n" % (name, mm.url, frmt,
                                                      hexport, himport)
    return "\n%s\n" % res


def table_exporter():
    """Generate the new exporter table."""
    res = (
        '| **Exporters Password Manager** | **Format** | **Command line** |\n'
        '|:------------------------------:|:----------:|:----------------:|\n'
    )

    matrix = MANAGERS.matrix(Cap.EXPORT)
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, md=True)
            res += "| [%s](%s) | %s | `pimport %s src [src]` |\n" % (
                name, mm.url, mm.format, name)
    return "\n%s\n" % res


def usage():
    """Generate the new pass-import usage."""
    string = io.StringIO()
    parser = ArgParser(True)
    parser.print_help(string)
    return "\n```\n%s```\n" % string.getvalue()


# Manual pages

def usage_importer(ext=True):
    """Generate the usage for importer."""
    res = ''
    matrix = MANAGERS.matrix()
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, ext, md=False)
            res += "\n.TP\n\\fB%s %s%s\\fP\nWebsite: \\fI%s\\fP\n\n" % (
                name, mm.format, mm.version, mm.url)
            res += mm.usage
            res += ("Export: %s\n\n"
                    "Command: %s\n" % (mm.hexport, mm.himport))
    return "\n%s" % res


def usage_exporter():
    """Generate the usage for exporter."""
    res = ''
    matrix = MANAGERS.matrix(Cap.EXPORT)
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, md=False)
            res += "\n.TP\n\\fB%s %s %s\\fP\nWebsite: \\fI%s\\fP\n\n" % (
                name, mm.format, mm.version, mm.url)
            res += mm.usage
            res += "Command: pimport %s src [src]\n" % name
    return "\n%s" % res


# Shell Completion

def bash_cmd(var, cap):
    """Re-generate command for bash completion."""
    res = "\n\tlocal %s=(" % var
    for name in sorted(MANAGERS.names(cap)):
        if len(res.split('\n').pop()) + len(name) + 1 < 74:
            res += "%s " % name
        else:
            res += '\n\t\t%s ' % name
    return res[:-1] + ')\n\t'


def bash_importer():
    """Re-generate importer command for bash completion."""
    return bash_cmd('importers', Cap.IMPORT)


def bash_exporter():
    """Re-generate exporter command for bash completion."""
    return bash_cmd('exporters', Cap.EXPORT)


def zsh_cmd(cap):
    """Re-generate command for zsh completion."""
    res = "\n\t\tsubcommands=(\n"
    matrix = MANAGERS.matrix(cap)
    for name in sorted(matrix):
        formats = []
        capability = 'Importer'
        for pm in matrix[name]:
            if cap is Cap.EXPORT:
                capability = 'Exporter'

            frmt = pm.format.upper()
            if pm.version:
                frmt += ' v%s' % pm.version
            formats.append(frmt)
        desc = '%s for %s in %s' % (capability, name, ', '.join(formats))
        res += "\t\t\t'%s:%s'\n" % (name, desc)
    return res + '\t\t)\n\t\t'


def zsh_importer():
    """Re-generate importer command for zsh completion."""
    return zsh_cmd(Cap.IMPORT)


def zsh_exporter():
    """Re-generate exporter command for zsh completion."""
    return zsh_cmd(Cap.EXPORT)


UPDATE = {
    'README.md': [
        ('<!-- NB BEGIN -->', '<!-- NB END -->', '%d' % len(MANAGERS)),
        ('<!-- LIST BEGIN -->', '<!-- LIST END -->', table_importer()),
        ('<!-- LIST DST BEGIN -->', '<!-- LIST DST END -->', table_exporter()),
        ('<!-- USAGE BEGIN -->', '<!-- USAGE END -->', usage()),
    ],
    'docs/pass-import.1': [
        (r'\# NB BEGIN', r'\# NB END', '\n%d\n' % len(MANAGERS)),
        (r'\# LIST BEGIN', r'\# LIST END', usage_importer()),
    ],
    'docs/pimport.1': [
        (r'\# NB BEGIN', r'\# NB END', '\n%d\n' % len(MANAGERS)),
        (r'\# NB EXPORT BEGIN', r'\# NB EXPORT END',
         '\n%d\n' % len(MANAGERS.names(Cap.EXPORT))),
        (r'\# LIST BEGIN', r'\# LIST END', usage_importer()),
        (r'\# LIST DST BEGIN', r'\# LIST DST END', usage_exporter()),
    ],
    'completion/pass-import.bash': [
        ('# importers begin', '# importers end', bash_importer()),
    ],
    'completion/pass-import.zsh': [
        ('# importers begin', '# importers end', zsh_importer()),
    ],
    'completion/pimport.bash': [
        ('# importers begin', '# importers end', bash_importer()),
        ('# exporter begin', '# importers begin', bash_exporter()),
    ],
    'completion/pimport.zsh': [
        ('# importers begin', '# importers end', zsh_importer()),
        ('# exporter begin', '# exporter end', zsh_exporter()),
    ],
}


def main():
    """Update the documentation files last usage and manager lists."""
    for path, pattern in UPDATE.items():
        with open(path, 'r') as file:
            data = file.read()

        for begin, end, res in pattern:
            data = replace(begin, end, data, res)

        with open(path, 'w') as file:
            file.write(data)


if __name__ == "__main__":
    main()
