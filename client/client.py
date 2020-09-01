import json, datetime, requests, string, re

API_URL = "http://127.0.0.1:5000"

#testing
TEST_EVENT_ID = "WUQFSS9V"
TEST_CREATOR_TOKEN = "ORDCXHZNMOZN7FKC8503XI1RQ2RQTCGHDO9MGFSQLD2MV0WYVJHNGGK639P9T89I"


def menu():
    """Menu loop""" #Courtesy of https://stackoverflow.com/questions/34192588/simple-menu-in-python-3
    choice ='0'
    print("Welcome to use Notikums, the ultimate event management platform!")
    print("--------------------------------")
    while True:
        print("Select 1 to get list of all events")
        print("Select 2 to get information about a specific event")
        print("Select 3 to create a new event")
        print("Select 4 to modify or delete event")
        print("Select 5 to list event attendees")
        print("Select 6 to join event")
        print("Select 7 to modify participation info or leave event")
        print("Select 8 to get information about a specific attendee")
        print("Select Q to quit program")
        print("--------------------------------")

        choice = input ("What do you want to do? ")

        if choice == "1":
            get_events()
        elif choice == "2":
            get_single_event()
        elif choice == "3":
            create_event()
        elif choice == "4":
            modify_event()
            #delete_event()
        elif choice == "5":
            get_event_attendees()
        elif choice == "6":
            create_attendee()
        elif choice == "7":
            modify_attendee()
            #delete_attendee()
        elif choice == "8":
            get_attendee()
        elif choice == "Q":
            break
        else:
            print("Invalid choice.")


def get_events():
    """Gets list of all events"""
    resp = requests.get(API_URL + "/event")
    body = resp.json()
    for event in body:
        print("Identifier: {}".format(event["identifier"]))
        print("Title: {}".format(event["title"]))
        print("Location: {}".format(event["location"]))
        print("Time: {}".format(event["time"]))
        print("Creator: {}".format(event["creator_name"]))
        print("Description: {}".format(event["description"]))
        print("Image: {}".format(event["image"]))
        print("--------------------------------")
    return


def get_single_event():
    """Get data for specific event"""

    while True:
        event_id = input("Enter event id: ")
        if event_id:
            break

    resp = requests.get(API_URL + "/event/{}".format(event_id))
    if resp.status_code == 200:
        event = resp.json()
        print("--------------------------------")
        print("Identifier: {}".format(event["identifier"]))
        print("Title: {}".format(event["title"]))
        print("Location: {}".format(event["location"]))
        print("Time: {}".format(event["time"]))
        print("Creator: {}".format(event["creator_name"]))
        print("Description: {}".format(event["description"]))
        print("Image: {}".format(event["image"]))
        print("--------------------------------")
        return
    print("Event does not exist!")
    print("--------------------------------")
    return


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

    while True: #TODO: validate time format
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

    resp = requests.post(API_URL + "/event", data=json.dumps(event_item), headers={"Content-type": "application/json"})
    if resp.status_code == 201:
        event = resp.json()

        print("--------------------------------")
        print("Success! Event created")
        print("Identifier: {}".format(event["identifier"]))
        print("Creator token: {}".format(event["creator_token"]))
        print("Title: {}".format(event["title"]))
        print("Location: {}".format(event["location"]))
        print("Time: {}".format(event["time"]))
        print("Creator: {}".format(event["creator_name"]))
        print("Description: {}".format(event["description"]))
        print("Image: {}".format(event["image"]))
        print("--------------------------------")
        return
    print("Something went wrong! Make sure the event information is given in the correct form.")
    print("--------------------------------")
    return


def modify_event():
    """Modify previously created event"""
    event_item = {}

    while True:
        event_id = input("Enter event id: ")
        if event_id:
            break

    while True:
        creator_token = input("Enter your creator token: ")
        if creator_token:
            break

    event_title = input("Title: ")
    event_item["title"] = event_title
    event_time = input("Time in ISO8601 format (yyyy-mm-ddT00:00:00+0000): ")
    event_item["time"] = event_time
    event_location = input("Location: ")
    event_item["location"] = event_location
    event_creator_name = input("Creator: ")
    event_item["creator_name"] = event_creator_name
    event_description = input("Description: ")
    event_item["description"] = event_description
    event_image = input("Image URL: ")
    event_item["image"] = event_image

    resp = requests.put(API_URL + "/event/{}".format(event_id), data=json.dumps(event_item), headers={"Content-type": "application/json", "Authorization": "Basic {}".format(creator_token)})
    
    if resp.status_code == 200:
        event = resp.json()
        print("--------------------------------")
        print("Success! Event updated.")
        print("Identifier: {}".format(event["identifier"]))
        print("Creator token: {}".format(event["creator_token"]))
        print("Title: {}".format(event["title"]))
        print("Location: {}".format(event["location"]))
        print("Time: {}".format(event["time"]))
        print("Creator: {}".format(event["creator_name"]))
        print("Description: {}".format(event["description"]))
        print("Image: {}".format(event["image"]))
        print("--------------------------------")
        return
    elif resp.status_code == 404:
        print("--------------------------------")
        print("Event not found")
        print("--------------------------------")
    elif resp.status_code == 401:
        print("--------------------------------")
        print("Unauthorized")
        print("--------------------------------")
    elif resp.status_code == 415: #TODO: returns if only some info is given
        print("--------------------------------")
        print("")
        print("--------------------------------")


def delete_event(event_id, creator_token):
    """Delete previously created event"""
    print("not implemented (yet)")

def get_event_attendees():
    """Get attendee list for specific event"""
    print("not implemented (yet)")

def get_attendee():
    """Get specific attendee for specific event"""
    print("not implemented (yet)")

def create_attendee():
    """Join event"""
    print("not implemented (yet)")

def modify_attendee():
    """Modify prevoiusly created attending information for specific user in specific event"""
    print("not implemented (yet)")

def delete_attendee():
    """Delete previously created attending information for specific user in specific event"""
    print("not implemented (yet)")

def get_event_image(event_id):
    """Get image for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/image".format(event_id))
    event = resp.json()
    print("Image: " + event["image"])

def add_event_image(event_id, creator_token):
    """Add or change image for specific event"""
    print("not implemented (yet)")

def delete_event_image(event_id, creator_token):
    """Delete image from specific event"""
    print("not implemented (yet)")

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


menu()




#create_event()

#get_event_description(TEST_EVENT_ID)

#get_event_image(TEST_EVENT_ID)

#get_event_location(TEST_EVENT_ID)

#get_event_time(TEST_EVENT_ID)


# TEST EVENT RESPONSE JSON
# {
#     'creator_token': 'ORDCXHZNMOZN7FKC8503XI1RQ2RQTCGHDO9MGFSQLD2MV0WYVJHNGGK639P9T89I',
#     'title': 'TITLE2',
#     'identifier': 'WUQFSS9V',
#     'time': '2020-08-08T00:00:00',
#     'location': 'LOCATION2',
#     'creator_name': 'CREATOR2',
#     'description': 'DESCRIPTION2',
#     'image': 'URL2'
# }