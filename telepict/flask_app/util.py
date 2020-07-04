import functools

from flask import render_template, current_app, session as flask_session
from ..db import Player

def inject_current_player(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        with current_app.db.session_scope() as session:
            if 'username' in flask_session:
                current_player = session.query(Player). \
                    filter_by(name=flask_session['username']).one_or_none()
            else:
                current_player = None
            return func(session, current_player, *args, **kwargs)
    return wrapped
