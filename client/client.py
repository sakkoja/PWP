import json, datetime, requests, string

API_URL = "http://127.0.0.1:5000"


def menu():
    """Menu loop""" #https://stackoverflow.com/questions/34192588/simple-menu-in-python-3
    choice ='0'
    print("Welcome to use Notikums, the ultimate event management platform!\n")
    while True:
        print("\n\n--------------------------------")
        print("1) to get list of all events")
        print("2) to get information about a specific event")
        print("3) to create a new event")
        print("4) to modify or delete event")
        print("5) to list event attendees")
        print("6) to join event")
        print("7) to modify participation info or leave event")
        print("8) to get information about a specific attendee")
        print("9) to delete previously created event")
        print("Q) to quit program")
        print("--------------------------------")

        choice = input("What do you want to do? ")

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
        elif choice == "9":
            delete_event()
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice.")


def get_events():
    """Gets list of all events"""
    resp = requests.get(API_URL + "/event")
    print("--------------------------------")
    print("All events")
    print("--------------------------------")
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
    elif resp.status_code == 404:
        print("Event does not exist!\n")
        return
    print("Something went wrong!\n")
    return


def create_event():
    """Creates a new event based on user input"""
    event_item = {}

    while True:
        event_title = input("Title: ")
        if event_title:
            event_item["title"] = event_title
            break
        print("Title is required.\n")
        continue

    while True: #TODO: validate time format
        event_time = input("Time in ISO8601 format (yyyy-mm-ddT00:00:00+0000): ")
        if event_time:
            try:
                event_time = datetime.datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S%z")
                event_item["time"] = event_time.strftime("%Y-%m-%dT%H:%M:%S%z")
                break
            except ValueError:
                print("Give time in ISO8601 format!\n")
                continue
        print("Time is required.\n")
        continue

    while True:
        event_location = input("Location: ")
        if event_location:
            event_item["location"] = event_location
            break
        print("Location is required.\n")
        continue

    event_creator_name = input("Creator: ")
    if event_creator_name:
        event_item["creator_name"] = event_creator_name

    event_description = input("Description: ")
    if event_description:
        event_item["description"] = event_description
    
    event_image = input("Image URL: ")
    if event_image:
        event_item["image"] = event_image

    resp = requests.post(API_URL + "/event", data=json.dumps(event_item), headers={"Content-type": "application/json"})
    if resp.status_code == 201:
        event = resp.json()
        print("--------------------------------")
        print("Success! Event created.\n")
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
    print("Something went wrong! Make sure the event information is given in the correct form.\n")
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
    if event_title:
        event_item["title"] = event_title

    while True:
        event_time = input("Time in ISO8601 format (yyyy-mm-ddT00:00:00+0000): ")
        if event_time:
            try:
                event_time = datetime.datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S%z")
                event_item["time"] = event_time.strftime("%Y-%m-%dT%H:%M:%S%z")
                break
            except ValueError:
                print("Give time in ISO8601 format!\n")
                continue
        break

    event_location = input("Location: ")
    if event_location:
        event_item["location"] = event_location

    event_creator_name = input("Creator: ")
    if event_creator_name:
        event_item["creator_name"] = event_creator_name

    event_description = input("Description: ")
    if event_description:
        event_item["description"] = event_description

    event_image = input("Image URL: ")
    if event_image:
        event_item["image"] = event_image

    resp = requests.put(API_URL + "/event/{}".format(event_id), data=json.dumps(event_item), headers={"Content-type": "application/json", "Authorization": "Basic {}".format(creator_token)})
    
    if resp.status_code == 200:
        event = resp.json()
        print("--------------------------------")
        print("Success! Event updated.\n")
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
        print("Event not found.\n")
    elif resp.status_code == 401:
        print("Unauthorized.\n")
    else:
        print("Failure! Event was not updated.\n")


def delete_event():
    """Delete previously created event"""

    while True:
        event_id = input("Enter event id: ")
        if event_id:
            break

    while True:
        creator_token = input("Enter your creator token: ")
        if creator_token:
            break

    resp = requests.delete(API_URL + "/event/{}".format(event_id), headers={"Authorization": "Basic {}".format(creator_token)})

    if resp.status_code == 204:
        print("Success! Event deleted.\n")
        return
    elif resp.status_code == 404:
        print("Event not found.\n")
    elif resp.status_code == 401:
        print("Unauthorized.\n")
    else:
        print("Failure! Event was not deleted.\n")


def get_event_attendees():
    """Get attendee list for specific event"""

    while True:
        event_id = input("Enter event id: ")
        if event_id:
            break

    while True:
        creator_token = input("Enter your creator token: ")
        if creator_token:
            break

    resp = requests.get(API_URL + "/event/{}/attendees".format(event_id), headers={"Authorization": "Basic {}".format(creator_token)})
    if resp.status_code == 200:
        body = resp.json()
        print("--------------------------------")
        print("Event attendees")
        print("--------------------------------")
        for user in body:
            print("Identifier: {}".format(user["user_identifier"]))
            print("Username: {}".format(user["user_name"]))
            print("First name: {}".format(user["first_name"]))
            print("Last name: {}".format(user["last_name"]))
            print("Email: {}".format(user["email"]))
            print("Phone: {}".format(user["phone"]))
            print("--------------------------------")
        return
    
    elif resp.status_code == 404:
        print("Event or user not found!\n")
    elif resp.status_code == 401:
        print("Unauthorized.\n")
    else:
        print("Failure!\n")


def get_attendee():
    """Get specific attendee for specific event"""

    while True:
        event_id = input("Enter event id: ")
        if event_id:
            break

    while True:
        user_id = input("Enter user id: ")
        if user_id:
            break

    while True:
        user_token = input("Enter your user token (or event creator token): ")
        if user_token:
            break

    resp = requests.get(API_URL + "/event/{}/attendees/{}".format(event_id, user_id), headers={"Authorization": "Basic {}".format(user_token)})
    if resp.status_code == 200:
        user = resp.json()
        print("Identifier: {}".format(user["user_identifier"]))
        print("Username: {}".format(user["user_name"]))
        print("First name: {}".format(user["first_name"]))
        print("Last name: {}".format(user["last_name"]))
        print("Email: {}".format(user["email"]))
        print("Phone: {}".format(user["phone"]))
        print("--------------------------------")
        return
    
    elif resp.status_code == 404:
        print("Event or user not found!\n")
    elif resp.status_code == 401:
        print("Unauthorized.\n")
    else:
        print("Failure!\n")


def create_attendee():
    """Join event"""

    while True:
        event_id = input("Enter event id for event you want to participate: ")
        if event_id:
            break

    user_item = {}

    while True:
        user_name = input("Username: ")
        if user_name:
            user_item["user_name"] = user_name
            break
        print("Username is required.\n")
        continue

    first_name = input("First name: ")
    if first_name:
        user_item["first_name"] = first_name

    last_name = input("Last name: ")
    if last_name:
        user_item["last_name"] = last_name
    
    email = input("Email: ")
    if email:
        user_item["email"] = email
    
    phone = input("Phone: ")
    if phone:
        user_item["phone"] = phone

    resp = requests.post(API_URL + "/event/{}/attendees".format(event_id), data=json.dumps(user_item), headers={"Content-type": "application/json"})
    if resp.status_code == 201:
        attendee = resp.json()
        print("--------------------------------")
        print("Success! You have joined the event.")
        print("Identifier: {}".format(attendee["user_identifier"]))
        print("User token: {}".format(attendee["user_token"]))
        print("Username: {}".format(attendee["user_name"]))
        print("First name: {}".format(attendee["first_name"]))
        print("Last name: {}".format(attendee["last_name"]))
        print("Email: {}".format(attendee["email"]))
        print("Phone: {}".format(attendee["phone"]))
        print("--------------------------------")
        return
    print("Something went wrong! Make sure the user information is given in the correct form.\n")
    return


def modify_attendee():
    """Modify prevoiusly created attending information for specific user in specific event"""

    while True:
        event_id = input("Enter event id for event you are participating: ")
        if event_id:
            break

    while True:
        user_id = input("Enter you user id: ")
        if user_id:
            break

    while True:
        user_token = input("Enter your user token (or event creator token): ")
        if user_token:
            break

    user_item = {}

    user_name = input("Username: ")
    if user_name:
        user_item["user_name"] = user_name

    first_name = input("First name: ")
    if first_name:
        user_item["first_name"] = first_name

    last_name = input("Last name: ")
    if last_name:
        user_item["last_name"] = last_name
    
    email = input("Email: ")
    if email:
        user_item["email"] = email
    
    phone = input("Phone: ")
    if phone:
        user_item["phone"] = phone

    resp = requests.put(API_URL + "/event/{}/attendees/{}".format(event_id, user_id), data=json.dumps(user_item), headers={"Content-type": "application/json", "Authorization": "Basic {}".format(user_token)})
    if resp.status_code == 200:
        attendee = resp.json()

        print("Success! Attendee info modified.")
        print("Identifier: {}".format(attendee["user_identifier"]))
        print("User token: {}".format(attendee["user_token"]))
        print("Username: {}".format(attendee["user_name"]))
        print("First name: {}".format(attendee["first_name"]))
        print("Last name: {}".format(attendee["last_name"]))
        print("Email: {}".format(attendee["email"]))
        print("Phone: {}".format(attendee["phone"]))
        print("--------------------------------")
        return
    elif resp.status_code == 404:
        print("Event or user not found!\n")
    elif resp.status_code == 401:
        print("Unauthorized.\n")
    else:
        print("Failure! Event was not deleted.\n")
    print("Something went wrong! Make sure the user information is given in the correct form.\n")
    return

# not implemented
def delete_attendee():
    """Delete previously created attending information for specific user in specific event"""

    while True:
        event_id = input("Enter event id for event you are participating: ")
        if event_id:
            break

    while True:
        user_id = input("Enter you user id: ")
        if user_id:
            break

    while True:
        user_token = input("Enter your user token (or event creator token): ")
        if user_token:
            break

    resp = requests.delete(API_URL + "/event/{}/attendees/{}".format(event_id, user_id), headers={"Authorization": "Basic {}".format(user_token)})

    if resp.status_code == 204:
        print("Success! Attendee deleted.\n")
        return
    elif resp.status_code == 404:
        print("Event or user not found.\n")
    elif resp.status_code == 401:
        print("Unauthorized.\n")
    else:
        print("Failure! Attendee was not deleted.\n")


# not implemented
def get_event_image(event_id):
    """Get image for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/image".format(event_id))
    event = resp.json()
    print("Image: " + event["image"])

# not implemented
def add_event_image(event_id, creator_token):
    """Add or change image for specific event"""
    print("not implemented (yet)\n")

# not implemented
def delete_event_image(event_id, creator_token):
    """Delete image from specific event"""
    print("not implemented (yet)\n")

# not implemented
def get_event_description(event_id):
    """Get description for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/description".format(event_id))
    event = resp.json()
    print("Description: " + event["description"])
    return

# not implemented
def get_event_location(event_id):
    """Get location for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/location".format(event_id))
    event = resp.json()
    print("Location: " + event["location"])
    return

# not implemented
def get_event_time(event_id):
    """Get time for single event by event_id"""
    resp = requests.get(API_URL + "/event/{}/time".format(event_id))
    event = resp.json()
    print("Time: " + event["time"])
    return


menu()