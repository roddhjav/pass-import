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

    def __init__(self, pm, md=True):
        self.pm = pm
        self.md = md

    def urlto_markdown(self, string):
        """Markdonize link."""
        if self.guide in string:
            msg = string.split(self.guide)
            url = msg.pop()
            string = ''.join(msg) + "[this guide](%s)" % url
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
                res = "`%s`" % self.pm.format
            else:
                res = "(%s)" % self.pm.format
        return res

    @property
    def version(self):
        """Get version formated."""
        res = ''
        if self.pm.version != '':
            if self.md:
                res = "`%s`" % self.pm.version
            else:
                res = "v%s" % self.pm.version
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
            res = '**pass import %s file.%s**' % (self.pm.name, self.pm.format)
        if not self.md:
            res = res.replace('**', '')
        return res

    @property
    def usage(self):
        """Get usage formated."""
        res = self.pm.usage()
        if res != '':
            res = "%s\n\n" % res
        return res

    @property
    def description(self):
        """Get description formated."""
        return self.pm.description()


# Generator functions
# --------------------

# README.md

def importers_nb():
    """Return a string of the importer len."""
    return "%d" % len(MANAGERS)


def markdown_table():
    """Generate the new supported table."""
    res = (
        '| **Password Manager** | **Format** | **v** | **How to export Data** | **Command line** |\n'  # noqa
        '|:--------------------:|:----------:|:-----:|:----------------------:|:----------------:|\n'  # noqa
    )

    matrix = MANAGERS.matrix()
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, md=True)
            res += "| [%s](%s) | %s | %s | *%s* | `%s` |\n" % (
                name, mm.url, mm.format, mm.version, mm.hexport, mm.himport)
    return "\n%s\n" % res


def helpmessage():
    """Generate the new pass-import usage."""
    string = io.StringIO()
    parser = ArgParser(True)
    parser.print_help(string)
    return "\n```\n%s```\n" % string.getvalue()


# pass-import.1

def importers_nb_line():
    """Return a line of the importer len."""
    return "\n%d\n" % len(MANAGERS)


def importers_usage():
    """Generate the new supported table."""
    res = ''
    matrix = MANAGERS.matrix()
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, md=False)
            res += "\n.TP\n\\fB%s %s %s\\fP\nWebsite: \\fI%s\\fP\n\n" % (
                name, mm.format, mm.version, mm.url)
            res += mm.usage
            res += ("Export: %s\n\n"
                    "Command: %s\n" % (mm.hexport, mm.himport))
    return "\n%s" % res


# Shell Completion

def bash_completion():
    """Re-generate command for bash completion."""
    res = "\n\tlocal importers=("
    for name in sorted(MANAGERS.names()):
        if len(res.split('\n').pop()) + len(name) + 1 < 74:
            res += "%s " % name
        else:
            res += '\n\t\t%s ' % name
    return res[:-1] + ')\n\t'


def zsh_completion():
    """Re-generate command for zsh completion."""
    res = "\n\t\tsubcommands=(\n"
    matrix = MANAGERS.matrix()
    for name in sorted(matrix):
        supported = []
        capability = 'Importer'
        for pm in matrix[name]:
            if Cap.EXPORT in pm.cap:
                capability = 'Importer & Exporter'
            support = pm.format.upper()
            if pm.version != '':
                support += ' v%s' % pm.version
            supported.append(support)
        desc = '%s for %s in %s' % (capability, name, ', '.join(supported))
        res += "\t\t\t'%s:%s'\n" % (name, desc)
    return res + '\t\t)\n\t\t'


UPDATE = {
    'README.md': [
        ('<!-- NB BEGIN -->', '<!-- NB END -->', importers_nb),
        ('<!-- LIST BEGIN -->', '<!-- LIST END -->', markdown_table),
        ('<!-- USAGE BEGIN -->', '<!-- USAGE END -->', helpmessage),
    ],
    'docs/pass-import.1': [
        (r'\# NB BEGIN', r'\# NB END', importers_nb_line),
        (r'\# LIST BEGIN', r'\# LIST END', importers_usage),
    ],
    'completion/pass-import.bash': [
        ('# importers begin', '# importers end', bash_completion),
    ],
    'completion/pass-import.zsh': [
        ('# subcommands begin', '# subcommands end', zsh_completion),
    ]
}


def main():
    """Update the documentation files last usage and importer list."""
    for path, pattern in UPDATE.items():
        with open(path, 'r') as file:
            data = file.read()

        for begin, end, fct in pattern:
            # print(fct())
            data = replace(begin, end, data, fct())

        with open(path, 'w') as file:
            file.write(data)


if __name__ == "__main__":
    main()
