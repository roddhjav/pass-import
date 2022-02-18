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
            string = ''.join(msg) + f'[this guide]({url})'
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
            string = ''.join(msg) + f'<a href="{url}">this guide</a>'
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
                res = f'({self.pm.format})'
            else:
                res = self.pm.format
        return res

    @property
    def version(self):
        """Get version formated."""
        res = ''
        if self.pm.version != '':
            res = f' v{self.pm.version}'
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
            res = f"{self.prog} {self.pm.name} file.{self.pm.format}"
        return res

    @property
    def usage(self):
        """Get usage formated."""
        res = self.pm.usage()
        if res != '':
            res = f'{res}\n\n'
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
    warning = "<!-- Do not edit manually, use 'make doc' instead. -->"
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

    return f"\n{warning}\n{table.render()}\n"


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
            res += (f"| [{name}]({mm.url}) | {mm.format} |"
                    f" `pimport {name} src [src]` |\n")
    return f"\n{res}\n"


def usage():
    """Generate the new pass-import usage."""
    string = io.StringIO()
    parser = ArgParser(True)
    parser.print_help(string)
    return f"\n```\n{string.getvalue()}```\n"


# Manual pages

def usage_importer(ext=True):
    """Generate the usage for importer."""
    res = ''
    matrix = MANAGERS.matrix()
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, ext, mode='man')
            res += (f"\n.TP\n\\fB{name} {mm.format}{mm.version}\\fP\n"
                    f"Website: \\fI{mm.url}\\fP\n\n")
            res += mm.usage
            res += (f"Export: {mm.hexport}\n\n"
                    f"Command: {mm.himport}\n")
    return "\n" + res


def usage_exporter():
    """Generate the usage for exporter."""
    res = ''
    matrix = MANAGERS.matrix(Cap.EXPORT)
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, mode='man')
            res += (f"\n.TP\n\\fB{name} {mm.format} {mm.version}\\fP\n"
                    f"Website: \\fI{mm.url}\\fP\n\n")
            res += mm.usage
            res += f"Command: pimport {name} src [src]\n"
    return "\n" + res


# Shell Completion

def bash_cmd(var, cap):
    """Re-generate command for bash completion."""
    res = f"\n\tlocal {var}=("
    for name in sorted(MANAGERS.names(cap)):
        if len(res.split('\n').pop()) + len(name) + 1 < 74:
            res += name + " "
        else:
            res += f'\n\t\t{name} '
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
                frmt += f' v{pm.version}'
            formats.append(frmt)
        desc = f"{capability} for {name} in {', '.join(formats)}"
        res += f"\t\t\t'{name}:{desc}'\n"
    return res + '\t\t)\n\t\t'


def zsh_importer():
    """Re-generate importer command for zsh completion."""
    return zsh_cmd(Cap.IMPORT)


def zsh_exporter():
    """Re-generate exporter command for zsh completion."""
    return zsh_cmd(Cap.EXPORT)


UPDATE = {
    'README.md': [
        ('<!-- NB BEGIN -->', '<!-- NB END -->', f'{len(MANAGERS)}'),
        ('<!-- LIST BEGIN -->', '<!-- LIST END -->', table_importer()),
        ('<!-- LIST DST BEGIN -->', '<!-- LIST DST END -->', table_exporter()),
        ('<!-- USAGE BEGIN -->', '<!-- USAGE END -->', usage()),
    ],
    'share/man/man1/pass-import.1': [
        (r'\# NB BEGIN', r'\# NB END', f'\n{len(MANAGERS)}\n'),
        (r'\# LIST BEGIN', r'\# LIST END', usage_importer()),
    ],
    'share/man/man1/pimport.1': [
        (r'\# NB BEGIN', r'\# NB END', f'\n{len(MANAGERS)}\n'),
        (r'\# NB EXPORT BEGIN', r'\# NB EXPORT END',
         f'\n{len(MANAGERS.names(Cap.EXPORT))}\n'),
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
