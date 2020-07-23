import os
import pytest
import tempfile
import app

from app import User, Event, Image
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event

@pytest.fixture
def basic_setup():
    # put the re-occuring setups in here and use this with each test
    pass

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    with app.app.app_context():
        app.db.create_all()

    yield app.db

    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

# tests

def test_create_users(db_handle):
    user = User(user_token="token", user_name="user_name")
    db_handle.session.add(user)
    db_handle.session.commit()
    assert User.query.count() == 1


def test_create_event(db_handle):
    event = Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here")
    db_handle.session.add(event)
    db_handle.session.commit()
    assert Event.query.count() == 1


def test_create_image(db_handle):
    image = Image(path="/dev/null")
    db_handle.session.add(image)
    db_handle.session.commit()
    assert Image.query.count() == 1