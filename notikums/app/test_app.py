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
test_events = []
test_users = []
EVENT_RESOURCE_URL = "/event"

def event_url(event_id):
    return "/event/{}".format(event_id)

def event_attendees_url(event_id):
    return event_url(event_id) + "/attendees"

def event_specific_attendee_url(event_id, attendee_id):
    return event_url(event_id) + "/attendees/{}".format(attendee_id)

def event_image(event_id):
    return event_url(event_id) + "/image"

def event_description(event_id):
    return event_url(event_id) + "/description"

def event_location(event_id):
    return event_url(event_id) + "/location"

def event_time(event_id):
    return event_url(event_id) + "/time"

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
            event=event,
            event_id=event.identifier,
            user_identifier="user-identifier-{}".format(i)
        )
        app.db.session.add(event)
        app.db.session.add(user)
        test_events.append(event.as_dict())
        test_users.append(user.as_dict())
    app.db.session.commit()

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()

    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    app.db.create_all()
    _populate_db()

    yield app.app.test_client()

    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

# tests

def test_get_root(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://notikums.docs.apiary.io/#"

def test_get_event_collection_positive(client):
    resp = client.get(EVENT_RESOURCE_URL)
    assert resp.status_code == 200
    for item in resp.json:
        assert "identifier" in item
        assert "title" in item
        assert "time" in item
        assert "location" in item

def test_get_event_positive(client):
    resp = client.get(event_url("identifier1"))
    assert resp.status_code == 200
    assert "identifier" in resp.json
    assert "title" in resp.json
    assert "time" in resp.json
    assert "location" in resp.json

def test_get_event_negative(client):
    resp = client.get(event_url("wrong_identifier"))
    assert resp.status_code == 404

def test_get_event_image_positive(client):
    resp = client.get(event_image("identifier1"))
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert "image" in resp.json

def test_get_event_image_negative(client):
    resp = client.get(event_image("wrong_identifier"))
    assert resp.status_code == 404

def test_get_event_desc_positive(client):
    resp = client.get(event_description("identifier1"))
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert "description" in resp.json

def test_get_event_desc_negative(client):
    resp = client.get(event_description("wrong_identifier"))
    assert resp.status_code == 404

def test_get_event_location_positive(client):
    resp = client.get(event_location("identifier1"))
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert "location" in resp.json

def test_get_event_location_negative(client):
    resp = client.get(event_location("wrong_identifier"))
    assert resp.status_code == 404

def test_get_event_time_positive(client):
    resp = client.get(event_time("identifier1"))
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert "time" in resp.json

def test_get_event_time_negative(client):
    resp = client.get(event_time("wrong_identifier"))
    assert resp.status_code == 404

def test_create_event_positive(client):
    result = client.post(
        EVENT_RESOURCE_URL,
        json={
            "title":"eventti",
            "time":"2020-02-02T00:00:00+0200",
            "location":"Tellus",
            "creator_name":"sakkoja",
            "description":"this is an event",
            "image":"http://google.com"
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    for assumed in ["creator_token", "identifier", "title"]:
        assert assumed in result.json

def test_create_event_negative(client):
    result = client.post(
        EVENT_RESOURCE_URL,
        json={
            "title":"eventti",
            "time":"2020-02-02T00:00:00+0200",
            "creator_name":"sakkoja",
            "description":"this is an event",
            "image":"http://google.com"
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    assert result.status_code == 415

def test_update_event_positive(client):
    # import pdb;pdb.set_trace()
    result = client.put(
        event_url(test_events[1].get("identifier")),
        json={
            "title": "new-title",
            "time": "2020-03-03T00:00:00+0200",
            "location": "new-location",
            "creator_name": "new-name",
            "description": "new-description",
            "image": "http://bing.com"
        },
        headers={
            "Authorization": "Basic " + test_events[1].get("creator_token")
        }
    )
    print(result)
    print(result.json)
    assert result.status_code == 200

def test_update_event_negative(client):
    result = client.put(
        event_url(test_events[1].get("identifier")),
        json={
            "title": "new-title"
        },
        headers={
            "Authorization": "Basic " + "probably_not_the_token_you_were_looking_for"
        }
    )
    print(result)
    print(result.json)
    assert result.status_code == 401

    result = client.put(
        event_url(test_events[1].get("identifier")),
        json={
            "title": "new-title",
            "time": "this time is too long for our JSON schema"
        },
        headers={
            "Authorization": "Basic " + test_events[1].get("creator_token")
        }
    )
    print(result)
    print(result.json)
    assert result.status_code == 415

    result = client.put(
        event_url("wrong_identifier"),
        json={
            "title": "new-title"
        },
        headers={
            "Authorization": "Basic " + test_events[1].get("creator_token")
        }
    )
    print(result)
    print(result.json)
    assert result.status_code == 404


def test_delete_event_positive(client):
    result = client.delete(
        event_url(test_events[1].get("identifier")),
        headers={
            "Authorization": "Basic " + test_events[1].get("creator_token")
        }
    )
    print(result)
    assert result.status_code == 204

def test_delete_event_negative(client):
    result = client.delete(
        event_url(test_events[1].get("identifier")),
        headers={
            "Authorization": "Basic " + "probably_not_the_token_you_were_looking_for"
        }
    )
    print(result)
    assert result.status_code == 401
    result = client.delete(
        event_url(test_events[1].get("wrong-identifier")),
        headers={
            "Authorization": "Basic " + "probably_not_the_token_you_were_looking_for"
        }
    )
    print(result)
    assert result.status_code == 404


def test_register_attendee_positive(client):
    result = client.post(
        event_attendees_url(test_events[0].get("identifier")),
        json={
            "user_name":"tester",
            "first_name": "first-tester",
            "last_name": "last-tester",
            "email": "test-email",
            "phone": "test-phone"
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    for assumed in ["user_token", "user_identifier"]:
        assert assumed in result.json


def test_register_attendee_negative(client):
    result = client.post(
        event_attendees_url("not-your-event"),
        json={
            "user_name":"tester"
        }
    )
    print(result)
    # what we assume we got in the response
    assert result.status_code == 404

    result = client.post(
        event_attendees_url(test_events[0].get("identifier")),
        json={
            "last_name":"tester"
        }
    )
    print(result)
    # what we assume we got in the response
    assert result.status_code == 415


def test_update_attendee_positive(client):
    result = client.put(
        event_specific_attendee_url(test_events[0].get("identifier"), test_users[0].get("user_identifier")),
        json={
            "user_name": "new-name",
            "first_name": "new-first",
            "last_name": "new-last",
            "email": "new-email",
            "phone": "new-phone"
        },
        headers={
            "Authorization": "Basic " + test_users[0].get("user_token")
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    assert result.status_code == 200
    assert result.json


def test_update_attendee_negative(client):
    result = client.put(
        event_specific_attendee_url(test_events[0].get("identifier"), test_users[0].get("user_identifier")),
        json={
            "user_name":"tester"
        },
        headers={
            "Authorization": "Basic " + "probably-not-the-toke-you-were-looking-for"
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    assert result.status_code == 401

    result = client.put(
        event_specific_attendee_url("wrong-identifier", "wrong-identifier"),
        json={
            "user_name":"tester"
        },
        headers={
            "Authorization": "Basic " + test_users[0].get("user_token")
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    assert result.status_code == 404

    result = client.put(
        event_specific_attendee_url(test_events[0].get("identifier"), test_users[0].get("user_identifier")),
        json={
            "user_name":"tester",
            "phone": "this phone number is too long for our JSON schema to not notice"
        },
        headers={
            "Authorization": "Basic " + test_users[0].get("user_token")
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    assert result.status_code == 415


def test_delete_attendee_positive(client):
    result = client.post(
        event_attendees_url(test_events[0].get("identifier")),
        json={
            "user_name":"tester"
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    for assumed in ["user_token", "user_identifier"]:
        assert assumed in result.json


def test_delete_attendee_negative(client):
    result = client.post(
        event_attendees_url(test_events[0].get("identifier")),
        json={
            "user_name":"tester"
        }
    )
    print(result)
    print(result.json)
    # what we assume we got in the response
    for assumed in ["user_token", "user_identifier"]:
        assert assumed in result.json


def test_get_single_attendee_positive(client):
    # get with the user_token
    result = client.get(
        event_specific_attendee_url(test_events[-1]["identifier"], test_users[-1]["user_identifier"]),
        headers={
            "Authorization": "Basic " + test_users[-1]["user_token"]
        }
    )
    assert result.status_code == 200
    for item in result.json:
        assert item in test_users[-1]

    # get with the creator_token
    result = client.get(
        event_specific_attendee_url(test_events[-1]["identifier"], test_users[-1]["user_identifier"]),
        headers={
            "Authorization": "Basic " + test_events[-1]["creator_token"]
        }
    )
    assert result.status_code == 200
    for item in result.json:
        assert item in test_users[-1]


def test_get_single_attendee_negative(client):
    result = client.get(
        event_specific_attendee_url(test_events[-1]["identifier"], test_users[-1]["user_identifier"]),
        headers={
            "Authorization": "Basic " + "probably_not_the_token_you_were_looking_for"
        }
    )
    assert result.status_code == 401
    # Not found
    result = client.get(
        event_specific_attendee_url(test_events[-1]["identifier"], "doesnt-exist"),
        headers={
            "Authorization": "Basic " + test_events[-1]["creator_token"]
        }
    )
    assert result.status_code == 404
    result = client.get(
        event_specific_attendee_url("doesnt-exist", test_users[-1]["user_identifier"]),
        headers={
            "Authorization": "Basic " + test_users[-1]["user_token"]
        }
    )
    assert result.status_code == 404


def test_get_all_attendees_posivive(client):
    # could perhaps create a separate test event with multiple attendees
    result = client.get(
        event_attendees_url(test_events[-1]["identifier"]),
        headers={
            "Authorization": "Basic " + test_events[-1]["creator_token"]
        }
    )
    assert result.status_code == 200
    for event in result.json:
        for item in event:
            assert item in test_users[-1]


def test_get_all_attendees_negative(client):
    # invalid token
    result = client.get(
        event_attendees_url(test_events[-1]["identifier"]),
        headers={
            "Authorization": "Basic " + "probably_not_the_token_you_were_looking_for"
        }
    )
    assert result.status_code == 401
    # inexistent event
    result = client.get(
        event_attendees_url("inexistent-event"),
        headers={
            "Authorization": "Basic " + test_events[-1]["creator_token"]
        }
    )
    assert result.status_code == 404


def test_update_image_positive(client):
    pass


def test_update_image_negative(client):
    pass
