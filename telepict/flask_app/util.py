import functools

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
