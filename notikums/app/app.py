import json, datetime, random, string, jsonschema, logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError
from flask_restful import Resource, Api
from jsonschema import validate

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notikums.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


### user authentication
def authenticate_user(client_token, stored_token):
    if client_token != ("Basic " + stored_token):
        return False
    return True


# logging for the application
logger = logging.getLogger("notikums")
logger.setLevel("DEBUG")
fh = logging.FileHandler(f"notikums_app.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy').addHandler(fh)


### utility
def validate_json(jsonData, jsonSchema):
    try:
        validate(instance=jsonData, schema=jsonSchema)
    except jsonschema.exceptions.ValidationError as err:
        logger.exception("validate_json(): schema validation resulted in error")
        return False
    return True

### schemas
def post_schema():
        schema = {
            "type": "object",
            "required": ["title", "time", "location"],
            # "optional": ["creator_name", "description", "image"]
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Title of event",
            "type": "string",
            "maxLength": 128
        }
        props["time"] = {
            "description": "Time and date of event",
            "type": "string",
            "minLength": 24,
            "maxLength": 24
        }
        props["location"] = {
            "description": "Location of event",
            "type": "string",
            "maxLength": 64
        }
        props["creator_name"] = {
            "description": "Name of the event creator",
            "type": "string",
            "maxLength": 64
        }
        props["description"] = {
            "description": "Description of event",
            "type": "string",
            "maxLength": 256
        }
        props["image"] = {
            "description": "Image of event",
            "type": "string",
            # "minLength": 0,
            "maxLength": 256
        }
        return schema


def image_post_schema():
    schema = schema = {
            "type": "object",
            "required": ["image"]
        }
    props = schema["properties"] = {}
    props["image"] = {
        "description": "Url of the event image",
        "type": "string",
        # "minLength": 0,
        "maxLength": 256
    }
    return schema


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    user_identifier = db.Column(db.String(8), unique=True, nullable=False) #this is exposed in API to identify users
    user_token = db.Column(db.String(64), nullable=False)
    user_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(16), nullable=True)

    event = db.relationship("Event", back_populates="attendees")

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    # def __repr__(self):
    #     return "{}".format(self.id, self.user_token)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(8), unique=True, nullable=False)  # this is exposed in API to identify events
    creator_name = db.Column(db.String(64), nullable=True)
    creator_token = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(64), nullable=False)
    image =  db.Column(db.String(256), nullable=True)

    attendees = db.relationship("User", back_populates="event")

    # credit to https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    # def __repr__(self):
    #     return "{},{},{},{}".format(self.id, self.title, self.time, self.location, self.creator_name, self.description)

def initialize_empty_database():
    db.create_all()


class ApiRoot(Resource):

    def get(self):
        """Notikums landing page and descriptions"""
        return "Well hello there. TODO: add apiary link here", 200


class EventCollection(Resource):

    def get(self):
        """get list of all events as JSON array"""
        try:
            response_data = []
            response_template = json.dumps(
                {
                    "title":"",
                    "identifier":"",
                    "time":"",
                    "location":"",
                    "creator_name":"",
                    "description":"",
                    "image":""
                })
            event_list = Event.query.all()
            for item in event_list:
                response_json = json.loads(response_template)
                response_json["title"] = item.title
                response_json["identifier"] = item.identifier
                response_json["time"] = (item.time).strftime("%Y-%m-%dT%H:%M:%S%z")
                response_json["location"] = item.location
                response_json["creator_name"] = item.creator_name
                response_json["description"] = item.description
                response_json["image"] = item.image
                response_data.append(response_json)
            return response_data, 200
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


    def post(self):
        """create new event"""

        # check if request is json and follows correct schema
        if not request.json or not validate_json(request.json, post_schema()):
            return "Request content type must be JSON", 415

        try:

            # create dict with empty values for all keys
            event_info = {"identifier": "", "creator_token": "", "title": "", "time": "", "location": "", "creator_name": "", "description": "", "image": ""}

            # check if request contains info and save the info to dict
            if "title" in request.json:
                event_info["title"] = request.json["title"]
            if "time" in request.json:
                event_info["time"] = datetime.datetime.strptime(request.json["time"], "%Y-%m-%dT%H:%M:%S%z")
            if "location" in request.json:
                event_info["location"] = request.json["location"]
            if "creator_name" in request.json:
                event_info["creator_name"] = request.json["creator_name"]
            if "description" in request.json:
                event_info["description"] = request.json["description"]
            if "image" in request.json:
                event_info["image"] = request.json["image"]

            # create secret token for creator to modify or delete event later
            event_info["creator_token"] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(64))

            # create unique event identifier 
            # TODO: check uniqueness before committing to db
            event_info["identifier"] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for j in range(8))

            # create new db entry for new event
            # TODO: change request handling to not save empty strings if value is not given
            new_event = Event(
                title=event_info["title"],
                identifier=event_info["identifier"],
                time=event_info["time"],
                location=event_info["location"],
                creator_name=event_info["creator_name"],
                creator_token=event_info["creator_token"],
                description=event_info["description"],
                image=event_info["image"]
            )

            # add and commit changes to db
            db.session.add(new_event)
            db.session.commit()

            # db query to return information about created event in response
            event_data = Event.query.filter_by(identifier=event_info["identifier"]).first()
            response_template = json.dumps(
                {
                    "creator_token": "",
                    "title":"",
                    "identifier":""
                })
            response_json = json.loads(response_template)
            response_json["creator_token"] = event_data.creator_token
            response_json["title"] = event_data.title
            response_json["identifier"] = event_data.identifier
            return response_json, 201
        except (KeyError, ValueError, OperationalError):
            return "Incomplete request - missing fields", 400

class EventItem(Resource):

    def get(self, event_id):
        """get specific event by id as JSON array"""

        # check if event exists and continue
        event_data = Event.query.filter_by(identifier=event_id).first()
        if not event_data:
            return "Event not found", 404

        try:
            response_template = json.dumps(
                {
                    "title":"",
                    "identifier":"",
                    "time":"",
                    "location":"",
                    "creator_name":"",
                    "description":"",
                    "image":""
                })
            response_json = json.loads(response_template)
            response_json["title"] = event_data.title
            response_json["identifier"] = event_data.identifier
            response_json["time"] = (event_data.time).strftime("%Y-%m-%dT%H:%M:%S%z")
            response_json["location"] = event_data.location
            response_json["creator_name"] = event_data.creator_name
            response_json["description"] = event_data.description
            response_json["image"] = event_data.image
            return response_json, 200
        except AttributeError:
            return "Event not found", 404
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


    def put(self, event_id):
        """modify event, requires creator token as header"""

        # check if request is json and follows correct schema
        if not request.json:
            return "Request content type must be JSON", 415

        # check if event exists and continue
        event_info = Event.query.filter_by(identifier=event_id).first()
        if not event_info:
            return "Event not found", 404

        # check authentication
        if not authenticate_user(request.headers.get("Authorization"), event_info.creator_token):
            return "Authorization failed", 401

        try:

            # check if request contains info and save the info
            if "title" in request.json:
                event_info.title = request.json["title"]
            if "time" in request.json:
                event_info.time = datetime.datetime.strptime(request.json["time"], "%Y-%m-%dT%H:%M:%S%z")
            if "location" in request.json:
                event_info.location = request.json["location"]
            if "creator_name" in request.json:
                event_info.creator_name = request.json["creator_name"]
            if "description" in request.json:
                event_info.description = request.json["description"]
            if "image" in request.json:
                event_info.image = request.json["image"]

            # commit changes to db and return 201
            db.session.commit()
            return "OK", 201
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "Incomplete request - missing fields", 400


    def delete(self, event_id):
        """delete event, requires creator token as header"""
        try:
            if not authenticate_user(request.headers.get("Authorization"), Event.query.filter_by(identifier=event_id).first().creator_token):
                return "Authorization failed", 401
            Event.query.filter_by(identifier=event_id).delete()
            db.session.commit()
            return "OK", 204
        except AttributeError:
            return "Event not found", 404


class AttendeeCollection(Resource):

#     # GET Requests
#     #
#     # Headers
#     # Authorization: Basic <creator_token>

#     # GET responses
#     # {
#     #     "event_id": "event1",
#     #     "attendee_list": {
#     #         "user1": {
#     #             "user_name": "user_name1",
#     #             "first_name": "Firstname-One",
#     #             "last_name": "Lastname-One",
#     #             "email": "userone@mail.email",
#     #             "phone": "+358100000000"
#     #         },
#     #         "user2": {
#     #             "user_name": "user_name2",
#     #             "first_name": "Firstname-Two",
#     #             "last_name": "Lastname-Two",
#     #             "email": "usertwo@mail.email",
#     #             "phone": "+358100000001"
#     #         }
#     #     }
#     # }
#     return "OK", 200

#     # nothing
#     return "Unauthorized", 401

#     # nothing
#     return "Not Found", 404


#     # POST Requests
#     #
#     # Headers
#     # Content-Type: application/json
#     #
#     # Body
#     # {
#     #     "user_name": "userone"
#     #     "first_name": "Firstname-One",
#     #     "last_name": "Lastname-One",
#     #     "email": "userone@mail.email",
#     #     "phone": "+358100000000"
#     # }

#     # POST Responses
#     # 
#     # {
#     #     "event_id": "event1",
#     #     "user_name": "userone"
#     #     "user_token": "asd321usertokenforevent1"
#     # }
#     return "Created", 201

#     # nothing
#     return "Bad Request", 400

#     # nothing
#     return "Not Found", 404


    def get(self, event_identifier):
        """get list of all attendees to specific event as JSON array"""

        event_item = Event.query.filter_by(identifier=event_identifier).first()
        if not event_item:
            return "Event not found", 404

        if not authenticate_user(request.headers.get("Authorization"), event_item.creator_token):
            return "Authentication failed", 401

        try:
            response_data = []
            response_template = json.dumps(
                {
                    "user_identifier":"",
                    "user_name":"",
                    "first_name":"",
                    "last_name":"",
                    "email":"",
                    "phone":""
                })
            for attendee in event_item.attendees:
                response_json = json.loads(response_template)
                response_json["user_identifier"] = attendee.user_identifier
                response_json["user_name"] = attendee.user_name
                response_json["first_name"] = attendee.first_name
                response_json["last_name"] = attendee.last_name
                response_json["email"] = attendee.email
                response_json["phone"] = attendee.phone
                response_data.append(response_json)
            return response_data, 200
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


    def post(self, event_identifier):
        """create new attendee to specific event"""
        event_item = Event.query.filter_by(identifier=event_identifier).first()
        if not event_item:
            return "Event not found", 404
        if not request.json:
            return "Request content type must be JSON", 415
        try:

            # create dict with empty values for all keys
            attendee_info = {"user_identifier": "", "user_token": "", "user_name": "", "first_name": "", "last_name": "", "email": "", "phone": ""}

            # check if request contains information and save that info to dict
            if "user_name" in request.json:
                attendee_info["user_name"] = request.json["user_name"]
            if "first_name" in request.json:
                attendee_info["first_name"] = request.json["first_name"]
            if "last_name" in request.json:
                attendee_info["last_name"] = request.json["last_name"]
            if "email" in request.json:
                attendee_info["email"] = request.json["email"]
            if "phone" in request.json:
                attendee_info["phone"] = request.json["phone"]

            # create secret token for user to modify or remove event participation later
            attendee_info["user_token"] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for j in range(64))

            # create unique user identifier
            # TODO: check uniqueness before committing to db
            attendee_info["user_identifier"] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(8))

            # create new db entry for new user
            # TODO: change request handling to not save empty strings if value is not given
            new_attendee = User(
                event=event_item,
                event_id=event_identifier,
                user_identifier=attendee_info["user_identifier"],
                user_token=attendee_info["user_token"],
                user_name=attendee_info["user_name"],
                first_name=attendee_info["first_name"],
                last_name=attendee_info["last_name"],
                email=attendee_info["email"],
                phone=attendee_info["phone"]
            )

            # add and commit changes to db
            db.session.add(new_attendee)
            db.session.commit()

            # db query to return user_identifier and user_token as response after joining event
            user_data = User.query.filter_by(user_identifier=attendee_info["user_identifier"]).first()
            response_template = json.dumps(
                {
                    "user_identifier":"",
                    "user_token": ""
                })
            response_json = json.loads(response_template)
            response_json["user_identifier"] = user_data.user_identifier
            response_json["user_token"] = user_data.user_token
            return response_json, 201
        # except (KeyError, ValueError, OperationalError):
        #     return "Incomplete request - missing fields", 400
        except (OperationalError):
            return "Incomplete request - missing fields", 400


class AttendeeItem(Resource):

# @app.route("/event/<event_id>/attendee/<user_name>", methods=["GET", "PUT", "DELETE"])
# def event_attendee(event_id):
#     """Event's attendees, visible to event's creator and attendee him/herself"""
#     # GET Requests
#     #
#     # Headers
#     # Authorization: Basic <creator_token> OR <user_token>

#     # GET responses
#     # 
#     # {
#     #     "user_name": "userone"
#     #     "first_name": "Firstname-One",
#     #     "last_name": "Lastname-One",
#     #     "email": "userone@mail.email",
#     #     "phone": "+358100000000"
#     # }
#     return "OK", 200

#     # nothing
#     return "Unauthorized", 401

#     # nothing
#     return "Not Found", 404


#     # PUT Requests
#     #
#     # Headers
#     # Authorization: Basic <user_token> OR <creator_token>
#     # Content-Type: application/json
#     #
#     # Body
#     # {
#     #     "user_name": "userone"
#     #     "first_name": "Firstname-One",
#     #     "last_name": "Lastname-One",
#     #     "email": "userone@mail.email",
#     #     "phone": "+358100000000"
#     # }


#     # DELETE Requests
#     #
#     # Headers
#     # Authorization: Basic <user_token> OR <creator_token>

#     # DELETE Responses
#     return "OK", 204

#     # nothing
#     return "Unauthorized", 401

#     # nothing
#     return "Not Found", 404

    def get(self, event_identifier, attendee_id):
        """get information of one attendee as JSON array"""

        event_item = Event.query.filter_by(identifier=event_identifier).first()
        if not event_item:
            return "Event not found", 404

        if not authenticate_user(request.headers.get("Authorization"), event_item.creator_token):
            attendee_item = User.query.filter_by(user_identifier=attendee_id).first()
            if not authenticate_user(request.headers.get("Authorization"), attendee_item.user_token):
                return "Authentication failed", 401

        try:
            response_data = []
            response_template = json.dumps(
                {
                    "user_identifier":"",
                    "user_name":"",
                    "first_name":"",
                    "last_name":"",
                    "email":"",
                    "phone":""
                })
            for attendee in event_item.attendees:
                response_json = json.loads(response_template)
                response_json["user_identifier"] = attendee.user_identifier
                response_json["user_name"] = attendee.user_name
                response_json["first_name"] = attendee.first_name
                response_json["last_name"] = attendee.last_name
                response_json["email"] = attendee.email
                response_json["phone"] = attendee.phone
                response_data.append(response_json)
            return response_data, 200
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


    def put(self, event_identifier, attendee_id):
        """modify attendee participation information"""

        # check if request is json and follows correct schema
        if not request.json:
            return "Request content type must be JSON", 415

        # check if event exists and continue
        event_item = Event.query.filter_by(identifier=event_identifier).first()
        if not event_item:
            return "Event not found", 404

        # check authentication, continue if request contains correct creator_token or user_token
        if not authenticate_user(request.headers.get("Authorization"), event_item.creator_token):
            attendee_item = User.query.filter_by(user_identifier=attendee_id).first()
            if not authenticate_user(request.headers.get("Authorization"), attendee_item.user_token):
                return "Authentication failed", 401

        try:

            # check if request contains information and save that info to dict
            if "user_name" in request.json:
                attendee_item.user_name = request.json["user_name"]
            if "first_name" in request.json:
                attendee_item.first_name = request.json["first_name"]
            if "last_name" in request.json:
                attendee_item.last_name = request.json["last_name"]
            if "email" in request.json:
                attendee_item.email = request.json["email"]
            if "phone" in request.json:
                attendee_item.phone = request.json["phone"]

            # commit changes to db and return 201
            db.session.commit()
            return 201

        except (KeyError, ValueError, OperationalError):
            return "Incomplete request - missing fields", 400


    def delete(self, event_identifier, attendee_id):
        """delete participation, requires """

        # check if request is json and follows correct schema
        if not request.json:
            return "Request content type must be JSON", 415

        # check if event exists and continue
        event_item = Event.query.filter_by(identifier=event_identifier).first()
        if not event_item:
            return "Event not found", 404

        # check authentication, continue if request contains correct creator_token or user_token
        if not authenticate_user(request.headers.get("Authorization"), event_item.creator_token):
            attendee_item = User.query.filter_by(user_identifier=attendee_id).first()
            if not authenticate_user(request.headers.get("Authorization"), attendee_item.user_token):
                return "Authentication failed", 401

        try:
            User.query.filter_by(user_identifier=attendee_id).delete()
            db.session.commit()
            return 204
        except (KeyError, ValueError, OperationalError):
            return "Incomplete request - missing fields", 400


class EventTime(Resource):

    def get(self, event_id):
        # # GET Responses
        # {
        #     "event_id": "event1",
        #     "time": "2020-01-01T00:00:00"
        # }
        # return "OK", 200
        # return "Not Found", 404
        """get time specific event by id as JSON array"""
        try:
            response_template = json.dumps(
                {
                    "time":""
                })
            event_data = Event.query.filter_by(identifier=event_id).first()
            response_json = json.loads(response_template)
            response_json["time"] = (event_data.time).strftime("%Y-%m-%dT%H:%M:%S%z")
            return response_json, 200
        except AttributeError:
            return "Event not found", 404
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


class EventLocation(Resource):

    def get(self, event_id):
        # # GEt Responses
        # {
        #     "event_id": "event1",
        #     "location": "LocationOne"
        # }
        # return "OK", 200
        # return "Not Found", 404
        """get location of specific event by id as JSON array"""
        try:
            response_template = json.dumps(
                {
                    "location":""
                })
            event_data = Event.query.filter_by(identifier=event_id).first()
            response_json = json.loads(response_template)
            response_json["location"] = event_data.location
            return response_json, 200
        except AttributeError:
            return "Event not found", 404
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


class EventDescription(Resource):

    def get(self, event_id):
        # # GET Responses
        # # {
        # #     "event_id": "event1",
        # #     "description": "This is an event"
        # # }
        # return "OK", 200
        # return "Not Found", 404
        """get description of specific event by id as JSON array"""
        try:
            response_template = json.dumps(
                {
                    "description":""
                })
            event_data = Event.query.filter_by(identifier=event_id).first()
            response_json = json.loads(response_template)
            response_json["description"] = event_data.description
            return response_json, 200
        except AttributeError:
            return "Event not found", 404
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


class EventImage(Resource):

    def get(self, event_id):
        """get image of specific event by id as JSON array"""
        # # GET responses
        # # {
        # #     "event_id": "event1",
        # #     "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
        # # }
        # return "OK", 200
        # return "Not Found", 404
        try:
            response_template = json.dumps(
                {
                    "image":""
                })
            event_data = Event.query.filter_by(identifier=event_id).first()
            response_json = json.loads(response_template)
            response_json["image"] = event_data.image
            return response_json, 200
        except AttributeError:
            return "Event not found", 404
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


    def post(self, event_id):
        # # POST Requests
        # Headers
        # Authorization: Basic asd123creatortokenforevent1
        # Content-Type: application/json
        # Body
        # "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
        # # POST Responses
        # # {
        # #     "event_id": "event1",
        # #     "image": "https://ouluhealth.fi/wp-content/uploads/2019/02/HIMMS_OuluSideEvent2019.jpg"
        # # }
        # return "Created", 201
        # return "Unauthorized", 401
        # return "Not Found", 404
        """add or modify image of event"""
        if not request.json or not validate_json(request.json, image_post_schema()):
            return "Request content type must be JSON", 415
        event = Event.query.filter_by(identifier=event_id).first()
        if not event:
            return "Not Found", 404
        if not authenticate_user(request.headers.get("Authorization"), event.creator_token):
            return "invalid token", 401
        try:
            event.image = request.json["image"]
            db.session.add(event)
            db.session.commit()
            event_data = Event.query.filter_by(identifier=event_id).first()
            response_template = json.dumps(
                {
                    "event_id": "",
                    "image":""
                })
            response_json = json.loads(response_template)
            response_json["event_id"] = event_data.identifier
            response_json["image"] = event_data.image
            logger.info("post image response: " + json.dumps(response_json))
            return response_json, 201
        except (KeyError, ValueError, OperationalError):
            return "Bad Request - https://http.cat/400", 400


    def delete(self, event_id):
        # # DELETE Requests
        # Headers
        # Authorization: Basic asd123creatortokenforevent1
        # Content-Type: application/json
        # # DELETE Responses
        # return "OK", 204
        # return "Unauthorized", 401
        # return "Not Found", 404
        """delete event image"""
        try:
            event = Event.query.filter_by(identifier=event_id).first()
            if not event:
                return "Not Found", 404
            if not authenticate_user(request.headers.get("Authorization"), event.creator_token):
                return "invalid token", 401
            event = Event.query.filter_by(identifier=event_id).first()
            event.image = None
            db.session.add(event)
            db.session.commit()
            return "OK", 204
        except AttributeError:
            return "Event not found", 404

db.create_all()
api.add_resource(ApiRoot, "/")
api.add_resource(EventCollection, "/event")
api.add_resource(EventItem, "/event/<event_id>")
api.add_resource(AttendeeCollection, "/event/<event_identifier>/attendees")
api.add_resource(AttendeeItem, "/event/<event_identifier>/attendees/<attendee_id>")
api.add_resource(EventTime, "/event/<event_id>/time")
api.add_resource(EventLocation, "/event/<event_id>/location")
api.add_resource(EventDescription, "/event/<event_id>/description")
api.add_resource(EventImage, "/event/<event_id>/image")


# create event with POST
# curl -i -X POST -H 'Content-Type: application/json' --data @<json_filename>.json http://localhost:5000/event



# Modify event with PUT
# curl -i -X PUT -H 'Content-Type: application/json' -H 'Authorization: Basic <creator_token>' --data @<json_filename>.json http://localhost:5000/event/<event_id>

# Get event attendee list
# curl -i -X GET -H 'Authorization: Basic <creator_token>' http://localhost:5000/event/<event_id>/attendees

# Create event attendee with POST
# curl -i -X POST -H 'Content-Type: application/json' -H 'Authorization: Basic <creator_token>' --data @<json_filename>.json http://localhost:5000/event/<event_id>


# Update event image
# curl -i -X POST -H "Content-Type: application/json" -H 'Authorization: Basic <creator_token>' --data '{"image": "/dev/null"}' localhost:5000/event/<event_id>/image

# Delete event image
# curl -i -X DELETE -H 'Authorization: Basic <creator_token>' localhost:5000/event/<event_id>/image

# Example json:
# {
#     "title":"eventti",
#     "time":"2020-02-02T00:00:00+0200",
#     "location":"Tellus",
#     "creator_name":"sakkoja",
#     "description":"this is an event",
#     "image":"http://google.com"
# }