#!/usr/bin/env python3

# Google Chrome/Chromium allows export to CSV. To enable this, go to
# chrome://flags/#password-import-export and set the option "Password import
# and export" to "Enabled". Restart chrome, open "chrome://settings/passwords"
# and click the "Export" button.
#
# If the above didn't work follow the instructions from this link
# https://www.axllent.org/docs/view/export-chrome-passwords/
#
# The CSV fields are: origin_url, hostname, username_value, password_value
#
# Usage: ./chrome2pass.py test.csv --prefix ChromeImport --username-format none|directory|at

import sys, argparse, itertools, csv, shlex
from subprocess import Popen, PIPE

parser = argparse.ArgumentParser(description='Import chrome passwords into passwordstore.')
parser.add_argument('--path-pattern', '-p', type=str, action='store', 
        help='A replacement pattern to generate the path name. Available variables: origin_url, hostname, username_value, password',
        default='{hostname}')
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

        if 'origin_url' in escaped_row:
            escaped_row['hostname'] = escaped_row['origin_url'].split('/')[2]

        for field in ['origin_url', 'username_value', 'password_value']:
            if not field in escaped_row or not escaped_row [field]:
                escaped_row [field] = 'NO-' + field.upper()
            escaped_row [field] = escaped_row [field].replace('/', '-')

        path = args.path_pattern.format(**escaped_row)

        data = row['password_value'] + '\n'
        for field in ['username_value', 'origin_url']:
            if field in row and row[field]: 
                data += '{}: {}\n'.format(field, row[field])

        pass_import_entry(path,data) 
