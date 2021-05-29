import os
import os.path
import secrets 
import argparse
import datetime
import re
import json

from dateutil.relativedelta import relativedelta

from telepict.config import Config
from telepict.auth import read_access_code_file, write_access_code_file

CODE_LENGTH = 64
lifetime_re = re.compile(r'(^\d+)([smhdwMY])')

unit_mapping = {'s': 'seconds',
                'm': 'minutes',
                'h': 'hours',
                'd': 'days',
                'w': 'weeks',
                'M': 'months',
                'Y': 'years'}

def remove_expired_codes(d, now):
    expired = [k for k, v in d.items() if v < now]
    for k in expired:
        print(f'Removing code {k} (expired {d[k].isoformat()}')
        del d[k]

def parse_lifetime(s, now):
    m = lifetime_re.match(s)
    if not m:
        raise ValueError(f'Invalid lifetime: {s!r}')
    num, units = m.groups()
    num = int(num)
    kwargs = {unit_mapping[units]: num}
    return now + relativedelta(**kwargs)

def generate_url(code):
    return 'https://telephone-pictionary.net/auth/create_account?code=' + code

def generate_access_code(lifetime, now):
    return secrets.token_urlsafe(CODE_LENGTH), parse_lifetime(lifetime, now)

if __name__ == '__main__':
    d = os.path.abspath(os.path.dirname(Config.ACCESS_CODE_FILE))
    if not os.path.isdir(d):
        os.makedirs(d)

    parser = argparse.ArgumentParser(description='Generate an access code')
    parser.add_argument('lifetime', help='The lifetime of the code')
    args = parser.parse_args()

    now = datetime.datetime.utcnow()

    codes = read_access_code_file()
    print(f'Loaded {len(codes)} access codes from {Config.ACCESS_CODE_FILE}')
    remove_expired_codes(codes, now)

    new_code, expiration = generate_access_code(args.lifetime, now)
    codes[new_code] = expiration
    print(f'Generated new access code: {new_code} (expires {expiration.isoformat()})')
    print(f'Have users visit this URL:\n\n{generate_url(new_code)}')

    write_access_code_file(codes)
