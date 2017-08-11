#!/usr/bin/env python3
# pass import - Password Store Extension (https://www.passwordstore.org/)
# Copyright (C) 2017 Alexandre PUJOL <alexandre@pujol.io>.
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

import os
import sys
import csv
from xml.etree import ElementTree
from subprocess import Popen, PIPE
from collections import OrderedDict

if 'VERBOSE' not in os.environ or 'QUIET' not in os.environ:
    print("This program should only be called by 'pass import'.")
    exit(1)

VERBOSE = bool(int(os.environ['VERBOSE']))
QUIET = bool(int(os.environ['QUIET']))

GREEN = '\033[32m'
YELLOW = '\033[33m'
BRED = '\033[91m'
BGREEN = '\033[92m'
BYELLOW = '\033[93m'
BMAGENTA = '\033[95m'
BOLD = '\033[1m'
END = '\033[0m'

def verbose(msg):
    if VERBOSE:
        print("%s  .  %s%s" % (BMAGENTA, END, msg))

def message(msg):
    if not QUIET:
        print("%s  .  %s%s" % (BOLD, END, msg))

def msg(msg):
    if not QUIET:
        print("       %s" % msg)

def success(msg):
    if not QUIET:
        print("%s (*) %s%s%s%s" % (BGREEN, END, GREEN, msg, END))

def warning(msg):
    if not QUIET:
        print("%s  w  %s%s%s%s" % (BYELLOW, END, YELLOW, msg, END))

def error(msg):
    print("%s [x] %s%sError: %s%s" % (BRED, END, BOLD, END, msg))

def die(msg):
    error(msg)
    exit(1)

