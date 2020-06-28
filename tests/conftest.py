import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import db
from populate_db import populate_db
from config import Config

@pytest.fixture(scope='function', autouse=True)
def reset_test_db():
    engine = create_engine(Config.DB_URL)
    Session = sessionmaker(bind=engine)
    db.engine, db.Session = engine, Session
    db.Base.metadata.create_all(engine)
    populate_db()

@pytest.fixture(scope='function')
def test_session():
    with db.session_scope() as session:
        yield session

def get_player_by_name(name, session):
    return session.query(db.Player).filter_by(name=name).one()

@pytest.fixture(scope='function')
def elwood(test_session):
    return get_player_by_name('Elwood', test_session)

@pytest.fixture(scope='function')
def nathan(test_session):
    return get_player_by_name('Nathan', test_session)

@pytest.fixture(scope='function')
def david(test_session):
    return get_player_by_name('david', test_session)
