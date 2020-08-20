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

def test_create_users_positive(db_handle):
    user = User(user_token="token", user_name="user_name")
    db_handle.session.add(user)
    db_handle.session.commit()
    assert User.query.count() == 1


def test_create_event_positive(db_handle):
    event = Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here", identifier="12345678")
    db_handle.session.add(event)
    db_handle.session.commit()
    assert Event.query.count() == 1

def test_create_full_users_positive(db_handle):
    user = User(user_token="token", user_name="user_name", first_name="Test", last_name="User", email="testmail@test.com", phone="0441234567")
    db_handle.session.add(user)
    db_handle.session.commit()
    assert User.query.count() == 1

def test_create_full_event_positive(db_handle):
    event = Event(creator_token="token", creator_name="Creator MacLovin", description="This is a test event :)", title="test event", time=datetime.utcnow(), location="here", identifier="12345678", image="https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg")
    db_handle.session.add(event)
    db_handle.session.commit()
    assert Event.query.count() == 1


def test_create_users_negative(db_handle):
    # test that invalid users can't be added to the database
    users = [
        User(),
        User(user_token="token", user_name=None),
        User(user_token=None, user_name="user_name")
        #User(user_token="a" * 120, user_name="user_name"),  # do we want to enforce the lenght of columns? https://stackoverflow.com/questions/2317081/sqlalchemy-maximum-column-length
    ]
    for user in users:
        with pytest.raises(IntegrityError):
            db_handle.session.add(user)
            db_handle.session.commit()
        db_handle.session.rollback()


def test_create_event_negative(db_handle):
    events = [
        Event(),
        Event(creator_token="token", title="test event", time=datetime.utcnow(), location=None),
        Event(creator_token="token", title="test event", time=None, location="here"),
        Event(creator_token="token", title=None, time=datetime.utcnow(), location="here"),
        Event(creator_token=None, title="test event", time=datetime.utcnow(), location="here"),
        Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here", creator_name="RI18SnEMQJyoclWJ9siJ9PVY4Xx7ikneZsXy0O8DUPTuwKWqv6Xg4l1bsRfA6SAgV1PogTvtxFuCpsb6"),
        Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here", image=True),
        Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here", description=404)
        # Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here", ),
    ]
    for event in events:
        with pytest.raises(IntegrityError):
            db_handle.session.add(event)
            db_handle.session.commit()
        db_handle.session.rollback()


# def test_create_image_negative(db_handle):
#     with pytest.raises(IntegrityError):
#         db_handle.session.add(Image())
#         db_handle.session.commit()


def test_create_event_attendee(db_handle):
    event = Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here", identifier="12345678")
    attendee = User(user_token="token", user_name="user_name")
    # add the event for the attendee, should back populate to the events
    attendee.event = event
    db_handle.session.add(event)
    db_handle.session.add(attendee)
    db_handle.session.commit()
    assert Event.query.first().attendees[0] == attendee
#   event = Event(creator_token="token", title="test event", time=datetime.utcnow(), location="here")
#     attendees = []
#     for i in range(5):
#         attendee = User(user_token="token", user_name="user_name_" + str(i)
#         attendee.event = event
#         attendees.append(attendee)

#     # add the event for the attendee, should back populate to the events
#     # db_handle.session.add(event)
#     # db_handle.session.add(attendee)
#     # db_handle.session.commit()
#     assert Event.query.first().attendees[0] == attendee