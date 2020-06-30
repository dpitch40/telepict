from hashlib import pbkdf2_hmac
import secrets

from config import Config

def gen_password_hash(password, salt):
    hash_ = pbkdf2_hmac('sha512', password.encode('utf8'), salt, Config.HASH_ITERATIONS)
    return hash_

def gen_password_salt():
    return secrets.token_bytes(64)

def gen_password_hash_and_salt(password):
    salt = gen_password_salt()
    hash_ = gen_password_hash(password, salt)
    return hash_, salt
