#!/usr/bin/env python3
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017-2019 Alexandre PUJOL <alexandre@pujol.io>.
#

# This script will update the readme file in this repo.

import io
import pass_import


def replace(marker_begin, marker_end, string, newcontent):
    """Replace data inside string markers."""
    begin = string.find(marker_begin)
    end = string.find(marker_end)
    return string.replace(string[begin + len(marker_begin):end], newcontent)


def rspace(string):
    """Remove space from url in markdown string."""
    if '](' in string:
        begin = string.find('](')
        end = string.find(')')
        url_space = string[begin + 2:end]
        string = string.replace(url_space, url_space.replace(' ', ''))
    return string


def table():
    """Generate the new supported table."""
    res = ('| **Password Manager** | **How to export Data** | **Command line** |\n'  # noqa
           '|:--------------------:|:----------------------:|:----------------:|\n')  # noqa

    for importer in sorted(pass_import.importers):
        doc = pass_import.getdoc(importer)
        export = rspace(doc['export'])
        res += "| [%s](%s) | *%s* | `%s` |\n" % (importer, doc['url'],
                                                 export, doc['import'])
    return "\n%s" % res


def helpmessage():
    """Generate the new pass-import usage."""
    string = io.StringIO()
    parser = pass_import.argumentsparse()
    parser.print_help(string)
    return "\n```\n%s\n```\n" % string.getvalue()


def main():
    """Update the readme with last usage and importer list."""
    path = 'README.md'
    nb_importers = "%d" % len(pass_import.importers)
    supported_table = table()
    help_message = helpmessage()

    with open(path, 'r') as file:
        readme = file.read()

    readme = replace('<!-- NB BEGIN -->', '<!-- NB END -->',
                     readme, nb_importers)

    readme = replace('<!-- SUPPORTED LIST BEGIN -->',
                     '<!-- SUPPORTED LIST END -->',
                     readme, supported_table)

    readme = replace('<!-- USAGE BEGIN -->', '<!-- USAGE END -->',
                     readme, help_message)

    with open(path, 'w') as file:
        file.write(readme)


if __name__ == "__main__":
    main()
