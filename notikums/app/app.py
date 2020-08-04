import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notikums.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    user_token = db.Column(db.String(64), nullable=False)
    user_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(16), nullable=True)

    event = db.relationship("Event", back_populates="attendees")

    # def __repr__(self):
    #     return "{}".format(self.id, self.user_token)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_name = db.Column(db.String(64), nullable=True)
    creator_token = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(64), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey("image.id"), nullable=True)

    attendees = db.relationship("User", back_populates="event")
    image = db.relationship("Image", back_populates="event")

    # def __repr__(self):
    #     return "{},{},{},{}".format(self.product_id, self.id, self.qty, self.location)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), nullable=False)

    event = db.relationship("Event", back_populates="image")


def initialize_empty_database():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    """Notikums landing page"""
    return "Notikums temp page", 200


@app.route("/event", methods=["GET", "POST"])
def create_event():
    """Get list of incoming events or send POST request to create event"""
    # GET response
    # {
    #     "event_list": {
    #         "event1": {
    #             "title": "EventOne",
    #             "creator_name": "OrganizerOne",
    #             "time": "2020-01-01T00:00:00",
    #             "location": "LocationOne"
    #         },
    #         "event2": {
    #             "title": "EventTwo",
    #             "creator_name": "OrganizerTwo",
    #             "time": "2020-01-01T00:00:00",
    #             "location": "LocationTwo"
    #         }
    #     }
    # }

    # POST response
    # {
    #     "creator_token":"tokenOne123dsa123s13dsa321dsa"
    # }

    return "Notikums temp page", 200


@app.route("/event/<event_id>", methods=["GET", "PUT", "DELETE"])
def modify_event(event_id):
    """Get event info (GET), modify event (PUT), delete event (DELETE)"""
    # GET response

    # {
    #     "event_id": {
    #         "title": "EventOne",
    #         "creator_name": "OrganizerOne",
    #         "time": "2020-01-01T00:00:00",
    #         "location": "LocationOne",
    #         "description": "This is an event",
    #         "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
    #     }
    # }


    return "Notikums temp page", 200


@app.route("/event/<event_id>/attendee", methods=["GET", "PUT", "POST", "DELETE"])
def event_attendee(event_id):
    """Event's attendeee list, only visible to event's creator"""
    # GET Requests
    #
    # Headers
    # Authorization: Basic asd123creatortokenforevent1

    # POST Requests
    #
    # Headers
    # Content-Type: application/json
    #
    # Body




    # DELETE Requests
    #
    # Headers
    # Authorization: Basic asd123creatortokenforevent1
    # Content-Type: application/json


    # GET responses
    # {
    #     "event_id": "event1",
    #     "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
    # }
    return "OK", 200

    # nothing
    return "Not Found", 404


    # POST Responses

    # {
    #     "event_id": "event1",
    #     "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
    # }
    return "Created", 201

    # nothing
    return "Unauthorized", 401

    # nothing
    return "Not Found", 404


    # DELETE Responses
    return "OK", 204

    # nothing
    return "Unauthorized", 401

    # nothing
    return "Not Found", 404





@app.route("/event/<event_id>/image", methods=["GET", "POST", "DELETE"])
def event_image(event_id):
    """get (GET), add (POST) or delete (DELETE) event image"""
    # POST Requests
    #
    # Headers
    # Authorization: Basic asd123creatortokenforevent1
    # Content-Type: application/json
    #
    # Body
    # "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
    
    # DELETE Requests
    #
    # Headers
    # Authorization: Basic asd123creatortokenforevent1
    # Content-Type: application/json


    # GET responses
    # {
    #     "event_id": "event1",
    #     "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
    # }
    return "OK", 200

    # nothing
    return "Not Found", 404


    # POST Responses

    # {
    #     "event_id": "event1",
    #     "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
    # }
    return "Created", 201

    # nothing
    return "Unauthorized", 401

    # nothing
    return "Not Found", 404


    # DELETE Responses
    return "OK", 204

    # nothing
    return "Unauthorized", 401

    # nothing
    return "Not Found", 404

@app.route("/event/<event_id>/description", methods=["GET"])
def event_description(event_id):
    """Get event description"""

    # GET Responses
    # {
    #     "event_id": "event1",
    #     "description": "This is an event"
    # }
    return "OK", 200

    # nothing
    return "Not Found", 404


@app.route("/event/<event_id>/location", methods=["GET"])
def event_location(event_id):
    """Get event location (GET)"""

    # GEt Responses
    # {
    #     "event_id": "event1",
    #     "location": "LocationOne"
    # }
    return "OK", 200

    # nothing
    return "Not Found", 404


@app.route("/event/<event_id>/time", methods=["GET"])
def event_time(event_id):
    """Get event time (GET)"""

    # GET Responses
    # {
    #     "event_id": "event1",
    #     "time": "2020-01-01T00:00:00"
    # }
    return "OK", 200

    # nothing
    return "Not Found", 404