from hashlib import sha3_512
import secrets

def gen_password_hash(password, salt):
    hash_ = sha3_512()
    hash_.update(password.encode('utf8'))
    hash_.update(salt)
    return hash_.digest()

def gen_password_salt():
    return secrets.token_bytes(64)

def gen_password_hash_and_salt(password):
    salt = gen_password_salt()
    hash_ = gen_password_hash(password, salt)
    return hash_, salt
