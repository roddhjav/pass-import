#!/usr/bin/env python3
# -*- coding: utf-8 -*
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

import io
import os
import sys
import traceback
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from pass_import import Detecters, Managers, __version__
from pass_import.auto import AutoDetect
from pass_import.core import Cap
from pass_import.errors import FormatError, PMError
from pass_import.tools import Config, get_magics

MANAGERS = Managers()


class ArgParser(ArgumentParser):
    """Manages argument parsing and adds some defaults."""

    def __init__(self, passwordstore=False):
        self.passwordstore = passwordstore
        if self.passwordstore:
            prog = 'pass import'
            description = """
  Import data from most of the password manager. Passwords are imported into
  the existing default password store; therefore, the password store must have
  been initialised before with 'pass init'."""
        else:
            prog = 'pimport'
            description = """
  Import data from most of the password manager. Passwords are imported into
  an existing password repository; therefore, the password repository must have
  been initialised before."""

        super().__init__(
            prog=prog,
            description=description,
            formatter_class=RawDescriptionHelpFormatter,
            epilog="More information may be found in the "
                   f"{prog.replace(' ', '-')}(1) man page.",
            add_help=False)
        self.add_arguments()

    def add_arguments(self):
        """Set arguments for `pass import` or `pimport`."""
        pmarg = self.add_argument_group(title='Password managers')
        if not self.passwordstore:
            pmarg.add_argument(
                'dst', type=str, nargs='?', default='',
                help=("Destination password manager, can be: "
                      f"{', '.join(MANAGERS.names(Cap.EXPORT))}."))

        pmarg.add_argument(
            'src', type=str, nargs='*', default=[],
            help='Path to the data to import. Can also be the password manager'
                 ' name followed by the path to the data to import. The passw'
                 f"ord manager name can be: {', '.join(MANAGERS.names())}.")

        if not self.passwordstore:
            pmarg.add_argument(
                '-o', '--out', action='store', default='',
                help='Where the destination password manager lives. '
                     'Can be a file, a directory or even a login depending '
                     'of the manager.')

        # Common options
        common = self.add_argument_group(title='Common optional arguments')
        common.add_argument(
            '-r', '--root', action='store', dest='sroot',
            default='', metavar='path',
            help='Only import the password from a specific subfolder.')
        common.add_argument(
            '-p', '--path', action='store', dest='droot',
            default='', metavar='path',
            help='Import the passwords to a specific subfolder.')
        common.add_argument('-k', '--key', action='store', default='',
                            help='Path to a keyfile if required by a manager.')
        common.add_argument('-a', '--all', action='store_true',
                            help='Also import all the extra data present.')
        common.add_argument('-f', '--force', action='store_true',
                            help='Overwrite existing passwords.')
        common.add_argument('-c', '--clean', action='store_true',
                            help='Make the paths more command line friendly.')
        common.add_argument(
            '-C', '--convert', action='store_true',
            help='Convert invalid characters present in the paths.')
        common.add_argument(
            '-P', '--pwned', action='store_true',
            help='Check imported passwords against haveibeenpwned.com.')

        # Extra options
        extra = self.add_argument_group(title='Extra optional arguments')
        extra.add_argument(
            '--sep', dest='separator', metavar='CHAR', default='-',
            help="Provide a characters of replacement for the path separator. "
                 "Default: '-'")
        extra.add_argument(
            '--del', dest='delimiter', metavar='CHAR', default=',',
            help="Provide an alternative CSV delimiter character. "
                 "Default: ','")
        extra.add_argument(
            '--cols', action='store', default='',
            help='CSV expected columns to map columns to credential attributes'
                 '. Only used by the csv importer.')
        extra.add_argument('--config', action='store', default='',
                           help="Set a config file. Default: '.import'")

        # Managers list
        usage = self.add_argument_group(
            title='Help related optional arguments')
        if self.passwordstore:
            usage.add_argument('-l', '--list', action='store_true',
                               help='List the supported password managers.')
        else:
            usage.add_argument('-l', '--list-importers', action='store_true',
                               help='List the supported password importers.')
            usage.add_argument('-e', '--list-exporters', action='store_true',
                               help='List the supported password exporters.')

        # Help and version
        usage.add_argument('-h', '--help', action='store_true',
                           help='Show this help message and exit.')
        usage.add_argument('-V', '--version', action='version',
                           version='%(prog)s ' + __version__,
                           help='Show the program version and exit.')
        group = usage.add_mutually_exclusive_group()
        group.add_argument('-v', '--verbose', action='count', default=0,
                           help='Set verbosity level, '
                                'can be used more than once.')
        group.add_argument('-q', '--quiet', action='store_true',
                           help='Be quiet.')

    def parse_args(self, args=None, namespace=None):
        """Parse pass-import arguments & print help."""
        if args is None:
            sys.argv.pop(0)
            args = sys.argv

        arg = vars(super().parse_args(args, namespace))
        arg['prog'] = self.prog
        if arg['help']:
            name = ''
            if self.passwordstore:
                if arg['src']:
                    name = arg['src'][0]
            else:
                name = arg['dst']

            if name in MANAGERS.names():
                self.print_help_manager(name)
            else:
                self.print_help()
            sys.exit(0)
        return arg

    def print_help_manager(self, name):
        """Print manager usage."""
        print(f'Usage: {self.prog} {name} [options]\n')
        for pm in MANAGERS.matrix().get(name):
            print(f'{pm.description()}:')
            usage = pm.usage()
            if usage:
                print(usage)
            if pm.format != '':
                print(f'  Format: {pm.format}')
            if pm.version != '':
                print(f'  Version: {pm.version}')
            if pm.url != '':
                print(f"  Url: {pm.url}")
            if pm.hexport != '':
                print(f'  Export: {pm.hexport}')
            if pm.himport != '':
                print(f'  Import: {pm.himport}')
            if pm.default:
                print(f'  This is the default importer for {name}.')
            if pm.cap is Cap.IMPORT | Cap.EXPORT:
                print('  Can be used for password import and export.')
            print()


def setup():
    """Read progam arguments, configuration & sanity checks."""
    conf = Config()
    parser = ArgParser(conf.passwordstore)
    arg = parser.parse_args()
    conf.verbosity(arg['verbose'], arg['quiet'])
    try:
        conf.readconfig(arg)
    except AttributeError as error:
        conf.verbose(error)
        conf.die("configuration file not valid.")
    conf.currate()

    if conf['list_importers'] or conf['list_exporters']:
        listmanagers(conf)

    if conf['exporter'] == '':
        conf.die("destination password manager not present.")

    if conf['exporter'] not in MANAGERS.names(Cap.EXPORT):
        conf.die(f"{conf['exporter']} is not a supported "
                 "destination password manager.")

    if not conf['src']:
        conf.die("The source password manager or the path to import is empty.")

    return conf


def listmanagers(conf):
    """List the supported password managers."""
    cap = Cap.IMPORT if conf['list_importers'] is True else Cap.EXPORT
    if conf.quiet:
        print('\n'.join(MANAGERS.names(cap)))
        sys.exit(0)

    if cap is Cap.EXPORT:
        msg = (f"The {len(MANAGERS.names(cap))} supported exporter "
               "password managers are:")
    else:
        msg = f"The {len(MANAGERS)} supported password managers are:"
    conf.success(msg)

    max_res = ''
    listing = {}
    matrix = MANAGERS.matrix(cap)
    for name in matrix:
        frmts = []
        for pm in matrix[name]:
            res = pm.format
            if pm.version:
                res += f' (v{pm.version})'
            max_res = max(max_res, res)
            frmts.append(res)
        listing[name] = frmts

    padding1 = len(max(MANAGERS.names(cap), key=len)) + 1
    if conf.verb:
        padding2 = len(max_res) + 1
        for name in sorted(matrix):
            for pm, frmt in zip(matrix[name], listing[name]):
                conf.message(conf.BOLD + name.ljust(padding1) + conf.end +
                             frmt.ljust(padding2) + pm.__name__)
    else:
        tmp = [', '.join(frmts) for frmts in listing.values()]
        padding2 = len(max(tmp, key=len)) + 1
        for name in sorted(listing):
            conf.message(conf.BOLD + name.ljust(padding1) + conf.end +
                         ', '.join(listing[name]).ljust(padding2) +
                         matrix[name][0].url)
    sys.exit(0)


def decryptsource(conf):
    """Decrypt source file if required."""
    path = conf['src'][1] if len(conf['src']) >= 2 else conf['src'][0]
    if os.path.isfile(path):
        decrypters = Detecters(Cap.DECRYPT)
        frmt, encoding = get_magics(path)
        if encoding:
            conf['encoding'] = encoding
        if frmt in decrypters:
            with decrypters[frmt](path) as file:
                conf['plaintext'] = file.decrypt()
                conf['decrypted'] = True
            conf.verbose(f"Source file decrypted using {frmt}.")


def detectmanager(conf):
    """Detect file format and password manager."""
    prefix = ''
    if len(conf['src']) == 1:
        name = conf['src'][0]
        if name in MANAGERS.names():
            conf.verbose("Using default manager.")
            detect = AutoDetect(name)
            pm = detect.default()

        else:
            conf.verbose("Trying to guess file format and manager name.")
            prefix = to_detect = name
            if conf['decrypted']:
                to_detect = conf['plaintext']

            detect = AutoDetect(settings=conf.getsettings())
            pm = detect.manager(to_detect)
            if pm is None:
                conf.die("Unable to detect the manager. Please try with: "
                         f"{conf['prog']} <manager> {prefix}")

    else:
        name = conf['src'][0]
        prefix = conf['src'][1]
        if name in MANAGERS.names():
            conf.verbose("Trying to guess file format.")
            to_detect = prefix
            if conf['decrypted']:
                to_detect = conf['plaintext']

            detect = AutoDetect(name, settings=conf.getsettings())
            pm = detect.format(to_detect)

        elif name in MANAGERS.clsnames():
            pm = MANAGERS.get(name)
            conf.verbose(f"Using import class: {pm.__name__}.")

        else:
            conf.die(f"{name} is not a supported source password manager.")

    conf.verbose(f"Importer: {pm.name}, Format: {pm.format}, Version: "
                 f" {pm.version}")

    if 'plaintext' in conf:
        conf['in'] = io.StringIO(conf['plaintext'])
    else:
        conf['in'] = prefix
    conf['importer'] = pm.name
    return pm


def zxcvbn_parse(details):
    """Nicely print the results from zxcvbn."""
    sequence = ''
    for seq in details.get('sequence', []):
        sequence += f"{seq['token']}({seq['pattern']}) "
    res = f"Score {details['score']} ({details['guesses']} guesses). "
    return res + f"This estimate is based on the sequence {sequence}"


# pylint: disable=inconsistent-return-statements
def pass_import(conf, cls_import):
    """Import data."""
    try:
        settings = conf.getsettings(conf['sroot'])
        with cls_import(conf['in'], settings=settings) as importer:
            importer.parse()
            if not importer.secure:  # pragma: no cover
                conf.warning(f"The password manager {conf['importer']} has "
                             "been flagged as unsecure, you should update all "
                             "your newly imported credentials.")
            return importer.data

    except (FormatError, AttributeError, ValueError, TypeError) as error:
        conf.debug(traceback.format_exc())
        conf.warning(error)
        conf.die(
            f"{conf['in']} is not a valid exported {conf['importer']} file.")

    except ImportError as error:
        conf.verbose(error)
        err = (f"Importing {conf['importer']}, missing required dependency: "
               f"{error.name}\n"
               f"You can install it with:\n  'pip3 install {error.name}'")
        if error.name not in ['pykeepass']:
            err += f", or\n  'sudo apt-get install python3-{error.name}'"
        conf.die(err)

    except (PermissionError, PMError) as error:
        conf.debug(traceback.format_exc())
        conf.die(error)


def pass_export(conf, cls_export, data):
    """Insert cleaned data into the password repository."""
    paths = []
    try:
        settings = conf.getsettings(conf['droot'], Cap.EXPORT)
        with cls_export(conf['out'], settings=settings) as exporter:
            exporter.data = data
            exporter.clean(conf['clean'], conf['convert'])
            report = exporter.audit(conf['pwned'])
            for entry in exporter.data:
                pmpath = os.path.join(conf['droot'], entry.get(
                    'path', entry.get('title', '')))
                conf.show(entry)
                try:
                    exporter.insert(entry)
                except PMError as error:
                    conf.debug(traceback.format_exc())
                    conf.warning(f"Impossible to insert {pmpath} into "
                                 f"{conf['exporter']}: {error}")
                else:
                    paths.append(pmpath)
    except PMError as error:
        conf.debug(traceback.format_exc())
        conf.die(error)

    return paths, report


def report(conf, paths, audit):
    """Print final success report."""
    conf.success(f"Importing passwords from {conf['importer']} "
                 f"to {conf['exporter']}")
    conf.message(f"Passwords imported from: {conf['in']}")
    conf.message(f"Passwords exported to: {conf['out']}")
    if conf['sroot'] != '':
        conf.message(f"Root path: {conf['sroot']}")
    if conf['droot'] != '':
        conf.message(f"Root path: {conf['droot']}")
    conf.message(f"Number of password imported: {len(paths)}")
    if conf['convert']:
        conf.message("Forbidden chars converted")
        conf.message(f"Path separator used: {conf['separator']}")
    if conf['clean']:
        conf.message("Imported data cleaned")
    if conf['all']:
        conf.message("All data imported")
    for password, count in audit['breached']:
        conf.warning(f"Password breached {count} time(s): {password}")
    for password, details in audit['weak']:
        conf.warning(f"Weak password detected: {password} might be weak."
                     f" {zxcvbn_parse(details)}")
    for entry in audit['duplicated']:
        conf.warning(f"Duplicated passwords detected: "
                     f"{', '.join([item['path'] for item in entry])}")
    if paths:
        conf.message("Passwords imported:")
        paths.sort()
        for path in paths:
            conf.echo(path)


def main():
    """`pimport` and `pass import` common main."""
    conf = setup()
    decryptsource(conf)

    # Password managers detection
    cls_import = detectmanager(conf)
    cls_export = MANAGERS.get(conf['exporter'], cap=Cap.EXPORT)
    conf.verbose(f"Importing passwords from {cls_import.__name__} "
                 f"to {cls_export.__name__}")
    conf.verbose("Checking for breached passwords",
                 "on haveibeenpwned.com" if conf['pwned'] else '')

    # Import & export
    data = pass_import(conf, cls_import)
    paths, audit = pass_export(conf, cls_export, data)

    # Success!
    report(conf, paths, audit)


if __name__ == "__main__":
    main()
