import functools

from cryptography.fernet import Fernet
from flask import current_app, session as flask_session

from ..db import Player

def get_current_player(session):
    if 'username' in flask_session:
        current_player = session.query(Player). \
            filter_by(name=flask_session['username']).one_or_none()
    else:
        current_player = None
    return current_player

def inject_current_player(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        with current_app.db.session_scope() as session:
            return func(session, get_current_player(session), *args, **kwargs)
    return wrapped

def encrypt_with_secret_key(b):
    if 'ENCRYPTION_KEY' in current_app.config:
        f = Fernet(current_app.config['ENCRYPTION_KEY'])
        return f.encrypt(b).decode('utf8')
    else:
        return b

def decrypt_with_secret_key(s):
    if 'ENCRYPTION_KEY' in current_app.config:
        f = Fernet(current_app.config['ENCRYPTION_KEY'])
        return f.decrypt(s.encode('utf8'))
    else:
        return s
