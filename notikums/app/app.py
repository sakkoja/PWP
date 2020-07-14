import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notikums.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_token = db.Column(db.String(64), nullable=False)
    user_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(16), nullable=True)

    participants = db.relationship("Events", back_populates="attendees")

    # def __repr__(self):
    #     return "{}".format(self.id, self.user_token)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_name = db.Column(db.String(64), nullable=True)
    creator_token = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(64), nullable=False)
    image = db.Column(db.Integer, db.ForeignKey("image.id"))

    attendees = db.relationship("Users", back_populates="participants")
    image = db.relationship("Images", back_populates="event")

    # def __repr__(self):
    #     return "{},{},{},{}".format(self.product_id, self.id, self.qty, self.location)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256), nullable=False)

    event = db.relationship("Events", back_populates="image")


db.create_all()


@app.route("/", methods=["GET"])
def index():
    """Notikums landing page"""
    return "Notikums temp page", 200


@app.route("/event", methods=["POST"])
def create_event():
    """Send POST request to create event"""
    return "Notikums temp page", 200


@app.route("/event/<event_id>", methods=["GET", "PUT", "DELETE"])
def modify_event(event_id):
    """Get event info (GET), modify event (PUT), delete event (DELETE)"""
    return "Notikums temp page", 200


@app.route("/event/<event_id>/attendees", methods=["GET", "PUT", "POST", "DELETE"])
def event_attendees(event_id):
    """Event's attendeee list, only visible to event's creator"""
    return "Notikums temp page", 200


@app.route("/event/<event_id>/image", methods=["GET", "POST", "DELETE"])
def event_image(event_id):
    """get (GET), add (POST) or delete (DELETE) event image"""
    return "Notikums temp page", 200


@app.route("/event/<event_id>/description", methods=["GET"])
def event_description(event_id):
    """Get event description"""
    return "Notikums temp page", 200


@app.route("/event/<event_id>/location", methods=["GET"])
def event_location(event_id):
    """Get event location (GET)"""
    return "Notikums temp page", 200


@app.route("/event/<event_id>/time", methods=["GET"])
def event_time(event_id):
    """Get event time (GET)"""
    return "Notikums temp page", 200
