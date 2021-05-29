import os.path
from hashlib import pbkdf2_hmac
import secrets
import time
import json
from datetime import datetime

from flask import current_app

from ..config import Config

def gen_password_hash(password, salt):
    hash_ = pbkdf2_hmac('sha512', password.encode('utf8'), salt, Config.HASH_ITERATIONS)
    return hash_

def gen_password_salt():
    return secrets.token_bytes(64)

def gen_password_hash_and_salt(password):
    salt = gen_password_salt()
    hash_ = gen_password_hash(password, salt)
    return hash_, salt

def read_access_code_file():
    if not os.path.isfile(Config.ACCESS_CODE_FILE):
        d = dict()
    else:
        with open(Config.ACCESS_CODE_FILE, 'r') as fobj:
            d = json.load(fobj)
        for k, v in d.items():
            d[k] = datetime.fromisoformat(v)
    return d

def write_access_code_file(d):
    d = d.copy()
    for k, v in d.items():
        d[k] = v.isoformat()
    with open(Config.ACCESS_CODE_FILE, 'w') as fobj:
        return json.dump(d, fobj, indent=2)

def verify_access_code(name, code):
    time.sleep(1)
    file_exists = os.path.isfile(Config.ACCESS_CODE_FILE)
    if not file_exists:
        current_app.logger.warning('Failed to verify access code %r from %s '
            'because the file does not exist', code, name)
    else:
        codes = read_access_code_file()

        now = datetime.utcnow()

        if code not in codes:
            current_app.logger.warning('Bad access code from %s: %r', name, code)
        elif codes[code] < now:
            current_app.logger.warning('Expired access code from %s: %r', name, code)
        else:
            return True

    return False
