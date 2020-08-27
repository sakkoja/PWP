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

import json, datetime, requests, string, re

API_URL = "http://127.0.0.1:5000"


def get_events():
    """Gets list of all events"""

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

#testing
get_events()

def get_single_event(event_id):
    """Get data for specific event"""
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

#testing
get_single_event("AA1KGJ08")

def create_event():
    """Creates a new event based on user input"""
    event_item = {}

    while True:
        event_title = input("Title: ")
        if event_title:
            event_item["title"] = event_title
            break
        print("Title is required.")
        continue

    while True:
        event_time = input("Time in ISO8601 format (yyyy-mm-ddT00:00:00+0000): ")
        if event_time:
            event_item["time"] = event_time
            break
        print("Time is required.")
        continue

    while True:
        event_location = input("Location: ")
        if event_location:
            event_item["location"] = event_location
            break
        print("Location is required.")
        continue

    event_creator_name = input("Creator: ")
    event_item["creator_name"] = event_creator_name
    event_description = input("Description: ")
    event_item["description"] = event_description
    event_image = input("Image URL: ")
    event_item["image"] = event_image

    print(event_item)
    return requests.post(API_URL + "/event", data=json.dumps(event_item), headers={"Content-type": "application/json"})

#testing
resp = create_event()
print(resp)

def modify_event(event_id, creator_token):
    """Modify previously created event"""
    pass

def delete_event(event_id, creator_token):
    """Delete previously created event"""
    pass

def get_event_attendees(event_id, creator_token):
    """Get attendee list for specific event"""
    pass

def get_attendee(event_id, user_token, creator_token):
    """Get specific attendee for specific event"""
    pass

def create_attendee(event_id):
    """Join event"""
    pass

def modify_attendee(event_id, user_token, creator_token):
    """Modify prevoiusly created attending information for specific user in specific event"""
    pass

def delete_attendee(event_id, user_token, creator_token):
    """Delete previously created attending information for specific user in specific event"""
    pass

def get_event_image(event_id):
    """Get image for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/image".format(event_id))
    event = resp.json()
    print("Image: " + event["image"])
    return

def add_event_image(event_id, creator_token):
    """Add or change image for specific event"""
    pass

def delete_event_image(event_id, creator_token):
    """Delete image from specific event"""
    pass

def get_event_description(event_id):
    """Get description for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/description".format(event_id))
    event = resp.json()
    print("Description: " + event["description"])
    return


def get_event_location(event_id):
    """Get location for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/location".format(event_id))
    event = resp.json()
    print("Location: " + event["location"])
    return


def get_event_time(event_id):
    """Get time for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/time".format(event_id))
    event = resp.json()
    print("Time: " + event["time"])
    return