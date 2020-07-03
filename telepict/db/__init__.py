from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Game, Player, Stack, Writing, Drawing, GamePlayerAssn, PendingGame, \
    Invitation, PendingGamePlayerAssn
from .base import Base
from ..config import Config

class DB:
    def __init__(self):
        self.engine = create_engine(Config.DB_URL)
        self.session = sessionmaker(bind=self.engine)

    def create_schema(self):
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self, *args, **kwargs):
        session = self.session(*args, **kwargs)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def connection_scope(self):
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()
