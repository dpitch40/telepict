from contextlib import contextmanager

from .models import Directions, Game, Player, Stack, Writing, Drawing, GamePlayerAssn, PendingGame
from .base import Base, engine, Session

@contextmanager
def session_scope(*args, **kwargs):
    session = Session(*args, **kwargs)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def connection_scope():
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
