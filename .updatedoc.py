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
from dominate import tags
from dominate.util import raw

import pass_import
from pass_import.__main__ import ArgParser
from pass_import.core import Cap

MANAGERS = pass_import.Managers()


# Internal tools
# ---------------

def replace(marker_begin, marker_end, string, newcontent):
    """Replace data inside string markers."""
    begin = string.find(marker_begin)
    end = string.find(marker_end)
    return string.replace(string[begin + len(marker_begin):end], newcontent)


class ManagerMeta():
    """Generate curated password managers metadata."""
    guide = 'this guide: '

    def __init__(self, pm, ext=True, mode='md'):
        self.pm = pm
        self.man = mode == 'man'
        self.markdown = mode == 'md'
        self.html = mode == 'html'
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

    def urlto_html(self, string):
        """Convert to html link."""
        if self.guide in string:
            msg = string.split(self.guide)
            url = msg.pop()
            string = ''.join(msg) + "<a href=\"%s\">this guide</a>" % url
        return string

    def genrow(self):
        """Generate the html row."""
        tags.td(tags.code(self.format, self.version),
                align='center', __pretty=False)
        tags.td(tags.i(raw(self.hexport)), align='center', __pretty=False)
        tags.td(tags.code(self.himport), align='center', __pretty=False)

    @property
    def format(self):
        """Get format formated."""
        res = ''
        if self.pm.format != '':
            if self.man:
                res = '(%s)' % self.pm.format
            else:
                res = self.pm.format
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
        res = ''
        if self.markdown:
            res = self.urlto_markdown(self.pm.hexport)
        elif self.man:
            res = self.urlto_man(self.pm.hexport)
        elif self.html:
            res = self.urlto_html(self.pm.hexport)
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
    matrix = MANAGERS.matrix()
    with tags.table() as table:
        with tags.thead():
            tags.th('Password Manager', align="center")
            tags.th('Formats', align="center")
            tags.th('How to export Data', align="center")
            tags.th('Command line', align="center")
        with tags.tbody():
            for name in sorted(matrix):
                size = len(matrix[name])
                for idx, pm in enumerate(matrix[name]):
                    with tags.tr():
                        mm = ManagerMeta(pm, mode='html')
                        if idx == 0:
                            tags.td(tags.a(name, href=mm.url), rowspan=size,
                                    align="center", __pretty=False)
                        mm.genrow()

    return "\n%s\n" % table.render()


def table_exporter():
    """Generate the new exporter table."""
    res = (
        '| **Exporters Password Manager** | **Format** | **Command line** |\n'
        '|:------------------------------:|:----------:|:----------------:|\n'
    )

    matrix = MANAGERS.matrix(Cap.EXPORT)
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, mode='md')
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
            mm = ManagerMeta(pm, ext, mode='man')
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
            mm = ManagerMeta(pm, mode='man')
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
    'share/man/man1/pass-import.1': [
        (r'\# NB BEGIN', r'\# NB END', '\n%d\n' % len(MANAGERS)),
        (r'\# LIST BEGIN', r'\# LIST END', usage_importer()),
    ],
    'share/man/man1/pimport.1': [
        (r'\# NB BEGIN', r'\# NB END', '\n%d\n' % len(MANAGERS)),
        (r'\# NB EXPORT BEGIN', r'\# NB EXPORT END',
         '\n%d\n' % len(MANAGERS.names(Cap.EXPORT))),
        (r'\# LIST BEGIN', r'\# LIST END', usage_importer()),
        (r'\# LIST DST BEGIN', r'\# LIST DST END', usage_exporter()),
    ],
    'share/bash-completion/completions/pass-import': [
        ('# importers begin', '# importers end', bash_importer()),
    ],
    'share/zsh/site-functions/_pass-import': [
        ('# importers begin', '# importers end', zsh_importer()),
    ],
    'share/bash-completion/completions/pimport': [
        ('# importers begin', '# importers end', bash_importer()),
        ('# exporter begin', '# importers begin', bash_exporter()),
    ],
    'share/zsh/site-functions/_pimport': [
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
