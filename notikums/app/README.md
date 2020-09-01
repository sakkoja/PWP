Notikums - event organizing API
===============================

How to run:
-----------
```
FLASK_APP=app.py FLASK_ENV=development flask run
```
after which the application can be accessed through e.g. the Web Browser.

Running unit-tests:
-------------------
```
# just run them
pytest
# run with a bit of more info
pytest --verbose
# outputting also the stdout
pytest -s
# run a specific test
pytest -k <name_of_the_test>
# with coverage
pytest --cov-report html:cov_html --cov=./
# for easy look-around the sources and their coverage
<browser_of_your_choosing> cov_html/index.html
```


When in doubt, cURL:
-------------------
```
# get all of the events in the database
curl -X GET localhost:5000/events

# create a new event
curl -X POST -H "Content-Type: application/json" --data '{"stuff":"test","more":10,"people":5}' localhost:5000/events

# create event with POST and a nice file json
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
```
Useful tips for developing:
---------------------------
```
# While developing its nice to test the code e.g. by running through iPython:
ipython
from app import *
... and play around

# for a quick and dirty debug of a part of the code; include this line before the failing part:
import pdb;pdb.set_trace()
# help can be accessed with ? or h(elp)
# code can be executed like in a python interface normally, so testing is easy.
```