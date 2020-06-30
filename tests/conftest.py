import pytest

from db import DB, Player
from populate_db import populate_db
from config import Config

@pytest.fixture(scope='function', autouse=True)
def reset_test_db():
    d = DB()
    d.create_schema()
    populate_db(d)
    return d

@pytest.fixture(scope='function')
def test_session(reset_test_db):
    with reset_test_db.session_scope() as session:
        yield session

def get_player_by_name(name, session):
    return session.query(Player).filter_by(name=name).one()

@pytest.fixture(scope='function')
def elwood(test_session):
    return get_player_by_name('Elwood', test_session)

@pytest.fixture(scope='function')
def nathan(test_session):
    return get_player_by_name('Nathan', test_session)

@pytest.fixture(scope='function')
def david(test_session):
    return get_player_by_name('david', test_session)
