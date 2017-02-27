#!/usr/bin/env python3

# Google Chrome/Chromium allows export to CSV. To enable this, go to
# chrome://flags/#password-import-export and set the option "Password import
# and export" to "Enabled". Restart chrome, open "chrome://settings/passwords"
# and click the "Export" button.
#
# The CSV fields are: name, url, username, password
#
# Usage: ./chrome2pass.py test.csv --prefix ChromeImport --username-format none|directory|at

import sys, argparse, itertools, csv, shlex
from subprocess import Popen, PIPE

parser = argparse.ArgumentParser(description='Import chrome passwords into passwordstore.')
parser.add_argument('--path-pattern', '-p', type=str, action='store', 
        help='A replacement pattern to generate the path name. Available variables: name, url, username, password',
        default='{name}/{username}')
parser.add_argument('--dry-run', action='store_true', help='Do not actually import data')
parser.add_argument('CSV_FILE', help='Input CSV file, exported from chrome.')
args = parser.parse_args()

def pass_import_entry(path, data):
    proc = Popen(['pass', 'insert', '--multiline', path], stdin=PIPE, stdout=PIPE)
    proc.communicate(data.encode('utf8'))
    proc.wait()
    print("Added:", path)

with open(args.CSV_FILE, 'r') as input_file:
    for row in csv.DictReader(input_file):
        escaped_row = dict(**row)

        for field in ['password', 'username', 'url', 'name']:
            if not field in escaped_row or not escaped_row [field]:
                escaped_row [field] = 'NO-' + field.upper()
            escaped_row [field] = escaped_row [field].replace('/', '-')

        path = args.path_pattern.format(**escaped_row)

        data = row['password'] + '\n'
        for field in ['name', 'username', 'url']:
            if field in row and row[field]: 
                data += '{}: {}\n'.format(field, row[field])

        pass_import_entry(path,data) 
