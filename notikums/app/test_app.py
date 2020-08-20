import os
import pytest
import tempfile
import app

from app import User, Event
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def basic_setup():
    # put the re-occuring setups in here and use this with each test
    pass

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# @pytest.fixture
# def db_handle():
#     db_fd, db_fname = tempfile.mkstemp()
#     app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
#     app.app.config["TESTING"] = True

#     with app.app.app_context():
#         app.db.create_all()

#     yield app.db

#     app.db.session.remove()
#     os.close(db_fd)
#     os.unlink(db_fname)

def _populate_db():
    for i in range(1, 4):
        event = Event(
            title="test-event-{}".format(i),
            time=datetime.utcnow(),
            location="test-location{}".format(i),
            creator_token="creator_token{}".format(i),
            identifier="identifier{}".format(i)
        )
        user = User(
            user_token="token{}".format(i),
            user_name="user-name{}".format(i),
            event_id=event.id
        )
        app.db.session.add(event)
        app.db.session.add(user)
    app.db.session.commit()

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    # import pdb;pdb.set_trace()

    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    app.db.create_all()
    _populate_db()

    yield app.app.test_client()

    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

# tests

def test_create_event(client):
    # import pdb;pdb.set_trace()
    # client.get("/event").json
    pass


# TODO:
# * muokkaa projektin rakenne kunnolliseksi single filen sijaan.