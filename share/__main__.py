#!/usr/bin/env python3
# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2024 Alexandre PUJOL <alexandre@pujol.io>.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate release, update the readme, man & completion files in this repo."""

import io
import re
import subprocess  # nosec
import sys
from datetime import datetime
try:
    from dominate import tags
    from dominate.util import raw
except ImportError:
    print('Error: "dominate" is required to generate the README table')
    sys.exit(1)

import pass_import as ext
from pass_import.__main__ import ArgParser
from pass_import.core import Cap

MANAGERS = ext.Managers()


# Internal tools
# ---------------

def replace(marker_begin, marker_end, string, newcontent):
    """Replace data inside string markers."""
    begin = string.find(marker_begin)
    end = string.find(marker_end)
    return string.replace(string[begin:end + len(marker_end)],
                          marker_begin + newcontent + marker_end)


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
            res = self.pm.hexport
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
            res += f"### {name} {mm.format} {mm.version}\n"
            if mm.url:
                res += f"**Website:** *{mm.url}*\n"
            res += mm.usage + "\n"
            res += (f"**Export:** {mm.hexport}\n\n"
                    f"**Command:** {mm.himport}\n\n")
    return "\n" + res


def usage_exporter():
    """Generate the usage for exporter."""
    res = ''
    matrix = MANAGERS.matrix(Cap.EXPORT)
    for name in sorted(matrix):
        for pm in matrix[name]:
            mm = ManagerMeta(pm, mode='man')
            res += f"### {name} {mm.format} {mm.version}\n"
            if mm.url:
                res += f"**Website:** *{mm.url}*\n"
            res += mm.usage + "\n"
            res += f"**Command:** pimport {name} src [src]\n\n"
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


DOCS = {
    'README.md': [
        ('<!-- NB BEGIN -->', '<!-- NB END -->', f'{len(MANAGERS)}'),
        ('<!-- NB DST BEGIN -->', '<!-- NB DST END -->',
         f'{len(MANAGERS.names(Cap.EXPORT))}'),
        ('<!-- LIST BEGIN -->', '<!-- LIST END -->', table_importer()),
        ('<!-- LIST DST BEGIN -->', '<!-- LIST DST END -->', table_exporter()),
        ('<!-- USAGE BEGIN -->', '<!-- USAGE END -->', usage()),
    ],
    'share/man/man1/pass-import.md': [
        ('<!-- NB BEGIN -->', '<!-- NB END -->', f'{len(MANAGERS)}'),
        ('<!-- LIST BEGIN -->', '<!-- LIST END -->', usage_importer()),
    ],
    'share/man/man1/pimport.md': [
        ('<!-- NB BEGIN -->', '<!-- NB END -->', f'{len(MANAGERS)}'),
        ('<!-- NB EXPORT BEGIN -->', '<!-- NB EXPORT END -->',
         f'{len(MANAGERS.names(Cap.EXPORT))}'),
        ('<!-- LIST BEGIN -->', '<!-- LIST END -->', usage_importer()),
        ('<!-- LIST DST BEGIN -->', '<!-- LIST DST END -->', usage_exporter()),
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


def makedoc():
    """Update the documentation files last usage and manager lists."""
    for path, pattern in DOCS.items():
        with open(path, 'r') as file:
            data = file.read()

        for begin, end, res in pattern:
            data = replace(begin, end, data, res)

        with open(path, 'w') as file:
            file.write(data)


def git_add(path: str):
    """Add file contents to the index."""
    subprocess.call(["/usr/bin/git", "add", path], shell=False)  # nosec


def git_commit(msg: str):
    """Record changes to the repository."""
    subprocess.call(["/usr/bin/git", "commit", "-S", "-m", msg],
                    shell=False)  # nosec


def debian_changelog(version: str):
    """Update debian/changelog."""
    path = "debian/changelog"
    now = datetime.now()
    date = now.strftime('%a, %d %b %Y %H:%M:%S +0000')
    template = f"""{ext.__title__} ({version}-1) stable; urgency=medium

  * Release {ext.__title__} v{version}

 -- {ext.__author__} <{ext.__email__}>  {date}

"""
    with open(path, 'r') as file:
        data = file.read()
    with open(path, 'w') as file:
        file.write(template + data)
    git_add(path)


def makerelease():
    """Make a new release commit."""
    oldversion = ext.__version__
    version = sys.argv.pop()
    release = {
        'README.md': [
            (f'pass-import-{oldversion}', f'pass-import-{version}'),
            (f'pass import {oldversion}', f'pass import {version}'),
            (f'v{oldversion}', f'v{version}'),
        ],
        'pass_import/__about__.py': [
            ('__version__ = .*', f"__version__ = '{version}'"),
        ],
        'setup.cfg': [
            (f'version = {oldversion}', f'version = {version}'),
        ],
    }
    debian_changelog(version)
    for path, pattern in release.items():
        with open(path, 'r') as file:
            data = file.read()

        for old, new in pattern:
            data = re.sub(old, new, data)

        with open(path, 'w') as file:
            file.write(data)

        git_add(path)
    git_commit(f"Release {ext.__title__} {version}")


if __name__ == "__main__":
    if '--docs' in sys.argv:
        makedoc()
    elif '--release' in sys.argv:
        makerelease()
    else:
        print('Usage: python share [--docs] | [--release VERSION]')
        sys.exit(1)
