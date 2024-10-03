import os
from dotenv import load_dotenv
import pymongo
from pymongo.server_api import ServerApi
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password


# Load environment variables from .env file
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Database
db = client['users']
users_collection = db['candidate']
instructors_collection = db['instructors']


questions_db = client['Questions']
mcq_collection = questions_db['mcq']
coding_collection = questions_db['coding_test']

admin_db=client['AdminAuth']
admin_collection=admin_db['Admin Details']


feedback_db = client['Feedback']  
collection =feedback_db['Details']



from pymongo import MongoClient

from pymongo import MongoClient

class QuestionDB:
    def __init__(self):
        # Initialize MongoDB connection
        self.client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
        self.db = self.client['your_database_name']               # Replace with your database name
        self.mcq_collection = self.db['mcqs']                     # Collection for MCQs
        self.coding_collection = self.db['coding_questions']       # Collection for coding questions

    def insert_mcq(self, assessment_no, mcq_list):
        """
        Insert multiple MCQ questions into the MCQ collection.
        
        :param assessment_no: Assessment number to associate with the MCQs.
        :param mcq_list: List of dictionaries containing MCQ question data.
        :return: Tuple of (status, message)
        """
        try:
            # Prepare a list for bulk insertion
            mcq_documents = []
            for mcq in mcq_list:
                # Assuming each mcq is a dictionary
                mcq_doc = {
                    'assessment_no': assessment_no,
                    'question_text': mcq['question_text'],
                    'options': mcq['options'],
                    'answer': mcq['answer'],
                    'tags': mcq.get('tags', []),  # Use .get() to handle missing keys
                }
                mcq_documents.append(mcq_doc)

            mcq_collection.insert_many(mcq_documents)  # Use insert_many for bulk insertion
        
        except Exception as e:
            return False, f"Error inserting MCQ: {str(e)}"

    def insert_coding_question(self, assessment_no, coding_list):
        """
        Insert multiple coding questions into the coding collection.
        
        :param assessment_no: Assessment number associated with the coding questions.
        :param coding_list: List of dictionaries containing coding question data.
        :return: Tuple of (status, message)
        """
        try:
            # Prepare a list for bulk insertion
            coding_documents = []
            for coding_data in coding_list:
                # Assuming each coding_data is a dictionary
                coding_doc = {
                    'assessment_no': assessment_no,
                    'question_text': coding_data['question_text'],  # Ensure this key exists in coding_data
                    'tags': coding_data.get('tags', []),  # Use .get() to handle missing keys
                }
                coding_documents.append(coding_doc)

            # Insert all coding documents at once
            coding_collection.insert_many(coding_documents)
            return True, "Coding questions inserted successfully"
        except Exception as e:
            return False, f"Error inserting coding question: {str(e)}"



    def fetch_mcqs_by_assessment(self, assessment_no):
        """
        Fetch all MCQ questions associated with a specific assessment number.
        
        :param assessment_no: Assessment number to filter MCQs.
        :return: List of MCQ documents or error message.
        """
        try:
            mcqs = list(self.mcq_collection.find({'assessment_no': assessment_no}))  # Fetch MCQs
            if mcqs:
                return True, mcqs  # Return MCQs if found
            else:
                return False, "No MCQs found for this assessment number"
        except Exception as e:
            return False, f"Error fetching MCQs: {str(e)}"

class Admin:
    @staticmethod
    def get_admin_credentials(admin_id):
        """Fetch admin credentials from MongoDB."""
        return admin_collection.find_one({"admin_id": admin_id})


class FeedbackModel:
    @staticmethod
    def insert_feedback(data):
        """Insert feedback data into MongoDB."""
        collection.insert_one(data)

class Candidate:
    @staticmethod
    def add_candidate(candidate_data):
        return users_collection.insert_one(candidate_data)

    @staticmethod
    def find_candidate_by_email(email):
        return users_collection.find_one({"email": email})

    @staticmethod
    def verify_candidate_login(email, password):
    # Fetch the candidate from the database
        candidate = users_collection.find_one({"email": email})

        # Check if the candidate exists
        if candidate is None:
            return None  # Candidate not found

        # Check if the candidate is deactivated
        status = candidate.get('status')  # Use get to avoid KeyError
        if status == "deactivated":  # Check if the status is 'deactive'
            return "not activated, please contact instructor"
        
        # Check if the password is correct
        is_correct = check_password(password, candidate['password'])

        if is_correct:
            return candidate  # Return candidate information if login is successful

        return None  # Return None if the password is incorrect

    @staticmethod
    def update_password(email, new_password):
        users_collection.update_one(
            {'email': email},
            {'$set': {'password': make_password(new_password)}}
        )

    @staticmethod
    def update_status(email, new_status):
        result = users_collection.update_one(
            {'email': email},
            {'$set': {'status': new_status}}
        )
        return result.modified_count > 0  # Return True if the update was successful


    
    def get_all_candidates():
        """Retrieve all candidates from the collection."""
        candidates = list(users_collection.find())  # Convert cursor to list
        return candidates

# Instructor Model
class Instructor:
    @staticmethod
    def update_status(email, new_status):
        result = instructors_collection.update_one(
            {'email': email},
            {'$set': {'status': new_status}}
        )
        print("\n\n",result,"asdas")
        return result.modified_count > 0  # Return True if the update was successful


    @staticmethod
    def update_password(email, new_password):
        instructors_collection.update_one(
            {'email': email},
            {'$set': {'password': make_password(new_password)}}
        )
    
    @staticmethod
    def add_instructor(instructor_data):
        return instructors_collection.insert_one(instructor_data)

    @staticmethod
    def find_instructor_by_email(email):
        return instructors_collection.find_one({"email": email})

    @staticmethod
    def verify_instructor_login(email, password):
        instructor = instructors_collection.find_one({"email": email})

        # Check if the instructor exists
        if instructor:
            # Use a secure password verification method
            if check_password(password, instructor['password']):
                if instructor['status'] == 'activated':
                    return instructor  # Account is active
                else:
                    return "Account created but not activated. Please contact admin."  # Account not activated
        
        return False  # No such instructor found or password is incorrect

    @staticmethod
    def get_all_instructors():
        """Retrieve all instructors from the collection."""
        instructors = list(instructors_collection.find())  # Convert cursor to list
        return instructors
    
