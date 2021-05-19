import os.path
from hashlib import pbkdf2_hmac
import secrets
import time

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

def verify_access_code(name, code):
    time.sleep(1)
    file_exists = os.path.isfile(Config.ACCESS_CODE_FILE)
    if not file_exists:
        current_app.logger.warning('Failed to verify access code because the file does not exist')
    else:
        file_age = time.time() - os.path.getmtime(Config.ACCESS_CODE_FILE)
        recent_enough = file_age < Config.MAX_ACCESS_CODE_AGE
        if not recent_enough:
            current_app.logger.warning(
                'Failed to verify access code because the file is %.2f hours old', file_age / 3600)
        else:
            if open(Config.ACCESS_CODE_FILE).read().strip() == code:
                return True
            else:
                current_app.logger.warning('Invalid access code from %s: %s', name, code)
    return False
