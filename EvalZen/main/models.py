import os
from dotenv import load_dotenv
import pymongo
from pymongo.server_api import ServerApi

# Load environment variables from .env file
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Database
db = client['users']

# Collections for candidates and instructors
users_collection = db['candidate']
instructors_collection = db['instructors']
# Candidate Model
class Candidate:
    @staticmethod
    def add_candidate(candidate_data):
        return users_collection.insert_one(candidate_data)

    @staticmethod
    def find_candidate_by_email(email):
        return users_collection.find_one({"email": email})

    @staticmethod
    def verify_candidate_login(email, password):
        candidate = users_collection.find_one({"email": email})
        if candidate and candidate['password'] == password:
            return candidate
        return None
    
    def get_all_candidates():
        """Retrieve all candidates from the collection."""
        candidates = list(users_collection.find())  # Convert cursor to list
        return candidates

# Instructor Model
class Instructor:
    @staticmethod
    def add_instructor(instructor_data):
        return instructors_collection.insert_one(instructor_data)

    @staticmethod
    def find_instructor_by_email(email):
        return instructors_collection.find_one({"email": email})

    @staticmethod
    def verify_instructor_login(email, password):
        instructor = instructors_collection.find_one({"email": email})
        if instructor and instructor['password'] == password:
            return instructor
        return False
    
    @staticmethod
    def get_all_instructors():
        """Retrieve all instructors from the collection."""
        instructors = list(instructors_collection.find())  # Convert cursor to list
        return instructors
    
