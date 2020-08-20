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
    identifier = db.Column(db.String(8), unique=True, nullable=False) #this is exposed in API to identify events
    creator_name = db.Column(db.String(64), nullable=True)
    creator_token = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(64), nullable=False)
    image =  db.Column(db.String(256), nullable=True)

    attendees = db.relationship("User", back_populates="event")

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
        if not request.json or not validate_json(request.json, post_schema()):
            return "Request content type must be JSON", 415
        try:
            event_title = request.json["title"]
            event_time = datetime.datetime.strptime(request.json["time"], "%Y-%m-%dT%H:%M:%S%z")
            event_location = request.json["location"]
            event_creator_name = request.json["creator_name"]
            event_description = request.json["description"]
            event_image = request.json["image"]
            event_creator_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(64))
            event_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for j in range(8))
            new_event = Event(
                title=event_title,
                identifier=event_identifier,
                time=event_time,
                location=event_location,
                creator_name=event_creator_name,
                creator_token=event_creator_token,
                description=event_description,
                image=event_image
            )
            db.session.add(new_event)
            db.session.commit()
            event_data = Event.query.filter_by(identifier=event_identifier).first()
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
            event_data = Event.query.filter_by(identifier=event_id).first()
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
        if not request.json:
            return "Request content type must be JSON", 415
        if not authenticate_user(request.headers.get("Authorization"), Event.query.filter_by(identifier=event_id).first().creator_token):
            return 401
        try:
            event_title = request.json["title"]
            event_time = datetime.datetime.strptime(request.json["time"], "%Y-%m-%dT%H:%M:%S%z")
            event_location = request.json["location"]
            event_creator_name = request.json["creator_name"]
            event_description = request.json["description"]
            event_image = request.json["image"]
            event_data = Event.query.filter_by(identifier=event_id).first()
            #TODO: add check to what values to update
            event_data.title = event_title
            event_data.time = event_time
            event_data.location = event_location
            event_data.creator_name = event_creator_name
            event_data.description = event_description
            event_data.image = event_image
            db.session.commit()
            return 201
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "Incomplete request - missing fields", 400


    def delete(self, event_id):
        """delete event, requires creator token as header"""
        try:
            if not authenticate_user(request.headers.get("Authorization"), Event.query.filter_by(identifier=event_id).first().creator_token):
                return 401
            Event.query.filter_by(identifier=event_id).delete()
            db.session.commit()
            return 204
        except AttributeError:
            return "Event not found", 404


class AttendeeCollection(Resource):

# @app.route("/event/<event_id>/attendee", methods=["GET", "POST"])
# def event_attendee_list(event_id):
#     """Event's attendee list, only visible to event's creator"""
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


    def get(self, event_id):
        """get list of all attendees to specific event as JSON array"""
        
        if not authenticate_user(request.headers.get("Authorization"), Event.query.filter_by(identifier=event_id).first().creator_token):
            return 401
        try:
            response_data = []
            response_template = json.dumps(
                {
                    "user_name":"",
                    "first_name":"",
                    "last_name":"",
                    "email":"",
                    "phone":""
                })
            attended_event = Event.query.filter_by(identifier=event_id).first()
            for attendee in attended_event.attendees:
                response_json = json.loads(response_template)
                response_json["user_name"] = attendee.user_name
                response_json["first_name"] = attendee.first_name
                response_json["last_name"] = attendee.last_name
                response_json["email"] = attendee.email
                response_json["phone"] = attendee.phone
                response_data.append(response_json)
            return response_data, 200
#            return attended_event.attendees, 200
        except (KeyError, ValueError, IntegrityError, OperationalError):
            return "General error o7", 400


    def post(self, event_id):
        """create new attendee to specific event"""
        if not request.json:
            return "Request content type must be JSON", 415
        try:
            event_title = request.json["title"]
            event_time = datetime.datetime.strptime(request.json["time"], "%Y-%m-%dT%H:%M:%S%z")
            event_location = request.json["location"]
            event_creator_name = request.json["creator_name"]
            event_description = request.json["description"]
            event_image = request.json["image"]
            event_creator_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(64))
            event_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for j in range(8))
            new_attendee = Event(
                title=event_title,
                identifier=event_identifier,
                time=event_time,
                location=event_location,
                creator_name=event_creator_name,
                creator_token=event_creator_token,
                description=event_description,
                image=event_image
            )
            db.session.add(new_attendee)
            db.session.commit()
            event_data = Event.query.filter_by(identifier=event_identifier).first()
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

    def get(self):
        pass

    def post(self):
        pass


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
api.add_resource(AttendeeCollection, "/event/<event_id>/attendees")
api.add_resource(AttendeeItem, "/event/<event_id>/attendees/<attendee_id>")
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