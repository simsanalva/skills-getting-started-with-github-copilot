"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pymongo import MongoClient
from fastapi import Depends
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# MongoDB setup
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["mergington"]
activities_collection = db["activities"]

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    # Sports related activities
    "Soccer Team": {
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    # Artistic activities
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Drama Society": {
        "description": "Participate in theater productions and acting workshops",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    # Intellectual activities
    "Math Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 16,
        "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Engage in science experiments and academic competitions",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["william@mergington.edu", "sophia@mergington.edu"]
    }
}


# Pre-populate MongoDB if empty
if activities_collection.count_documents({}) == 0:
    for name, details in activities.items():
        doc = {"_id": name, **details}
        activities_collection.insert_one(doc)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    # Fetch all activities from MongoDB
    activities = {}
    for doc in activities_collection.find():
        name = doc.pop("_id")
        activities[name] = doc
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in doc["participants"]:
        raise HTTPException(status_code=400, detail="Already signed up for this activity")

    # Check max participants
    if len(doc["participants"]) >= doc["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activities_collection.update_one({"_id": activity_name}, {"$push": {"participants": email}})
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is signed up
    if email not in doc["participants"]:
        raise HTTPException(status_code=400, detail="Student not registered for this activity")

    # Remove student
    activities_collection.update_one({"_id": activity_name}, {"$pull": {"participants": email}})
    return {"message": f"Unregistered {email} from {activity_name}"}
