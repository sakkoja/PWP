# get list of events with GET
# curl -i -X GET http://localhost:5000/event

# create event with POST
# curl -i -X POST -H 'Content-Type: application/json' --data @<json_filename>.json http://localhost:5000/event

# Modify event with PUT
# curl -i -X PUT -H 'Content-Type: application/json' -H 'Authorization: Basic <creator_token>' --data @<json_filename>.json http://localhost:5000/event/<event_id>

# Get event attendee list with GET
# curl -i -X GET -H 'Authorization: Basic <creator_token>' http://localhost:5000/event/<event_id>/attendees

# Create event attendee with POST
# curl -i -X POST -H 'Content-Type: application/json' -H 'Authorization: Basic <creator_token>' --data @<json_filename>.json http://localhost:5000/event/<event_id>

# Update event image with PUT
# curl -i -X POST -H "Content-Type: application/json" -H 'Authorization: Basic <creator_token>' --data '{"image": "/dev/null"}' localhost:5000/event/<event_id>/image

# Delete event image with DELETE
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

import json, datetime, requests

API_URL = "http://127.0.0.1:5000"


def get_events():
    """Gets list of all events and returns events that are going to happen"""

    resp = requests.get(API_URL + "/event")
    body = resp.json()
    for event in body:
        print("Identifier: " + event["identifier"])
        print("Title: " + event["title"])
        print("Location: " + event["location"])
        print("Time: " + event["time"])
        print("Creator: " + event["creator_name"])
        print("Description: " + event["description"])
        print("Image: " + event["image"])
        print("--------------------")
    return

get_events()

def get_single_event(event_id):
    """Get data for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}".format(event_id))
    event = resp.json()
    print("Event " + event["identifier"] + " information")
    print("Title: " + event["title"])
    print("Location: " + event["location"])
    print("Time: " + event["time"])
    print("Creator: " + event["creator_name"])
    print("Description: " + event["description"])
    print("Image: " + event["image"])
    print("--------------------")
    return

get_single_event("AA1KGJ08")

def create_event():
    """Creates a new event based on user input and sends it to API"""
    event_item = {}

    while True:
        event_title = input("Title: ")
        if event_title:
            event_item["title"] = event_title
            break
        print("Title is required")
        continue

    while True:
        event_time = input("Time: ")
        if event_time:
            event_item["time"] = event_title
            break
        print("Time is required")
        continue

    while True:
        event_location = input("Location: ")
        if event_location:
            event_item["location"] = event_location
            break
        print("Location is required")
        continue

    print(event_item)
    #return requests.post(API_URL + "/event", data=json.dumps(event_item), headers={"Content-type": "application/json"})

create_event()

def modify_event():
    pass

def delete_event():
    pass

def get_event_attendees():
    pass

def get_attendee():
    pass

def create_attendee():
    pass

def modify_attendee():
    pass

def delete_attendee():
    pass

def get_event_image():
    pass

def add_event_image():
    pass

def delete_event_image():
    pass

def get_event_description():
    pass

def get_event_location():
    pass

def get_event_time():
    pass

