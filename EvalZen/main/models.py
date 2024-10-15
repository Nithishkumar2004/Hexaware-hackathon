from datetime import datetime
import os
from bson import ObjectId
from dotenv import load_dotenv
import gridfs
import pymongo
from pymongo.server_api import ServerApi
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
import base64


# Load environment variables from .env file
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Database
db = client['users']
users_collection = db['candidate']
instructors_collection = db['instructors']

fs = gridfs.GridFS(db)



questions_db = client['Questions']
mcq_collection = questions_db['mcq']
coding_collection = questions_db['coding_test']
assessment_collection=questions_db['Assessment']

admin_db=client['AdminAuth']
admin_collection=admin_db['Admin Details']


feedback_db = client['Feedback']  
collection =feedback_db['Details']



from pymongo import MongoClient

from pymongo import MongoClient

class QuestionDB:
    
    @staticmethod
    def insert_mcq(assessment_no, mcq_list):
        try:
            mcq_documents = [
                {
                    'assessment_no': assessment_no,
                    'question_text': mcq['question_text'],
                    'options': mcq['options'],
                    'answer': mcq['answer'],
                    'tags': mcq.get('tags', [])
                }
                for mcq in mcq_list
            ]
            mcq_collection.insert_many(mcq_documents)
            return True, "MCQ questions inserted successfully"
        except Exception as e:
            return False, f"Error inserting MCQ: {str(e)}"

    @staticmethod
    def insert_coding_question(assessment_no, coding_list):
        try:
            coding_documents = [
                {
                    'Assessment_name': assessment_no,
                    'question_text': coding_data['question_text'],
                    'tags': coding_data.get('tags', [])
                }
                for coding_data in coding_list
            ]
            coding_collection.insert_many(coding_documents)
            return True, "Coding questions inserted successfully"
        except Exception as e:
            return False, f"Error inserting coding question: {str(e)}"

    @staticmethod
    def insert_assessment(data):
        return assessment_collection.insert_one(data)

    @staticmethod
    def fetch_mcqs_by_assessment(assessment_no):
        try:
            mcqs = list(mcq_collection.find({'assessment_no': assessment_no}))
            if mcqs:
                return True, mcqs
            else:
                return False, "No MCQs found for this assessment number"
        except Exception as e:
            return False, f"Error fetching MCQs: {str(e)}"

    @staticmethod
    def candidate_get_all_assessment():
    # Find all assessments where 'status' is 'scheduled'
         return list(assessment_collection.find({'status': 'scheduled'}))

    @staticmethod
    def get_all_assessment():
        return list(assessment_collection.find())

    @staticmethod
    def get_assessment(assessment_name):
        return assessment_collection.find_one({"assessment_name": assessment_name})

    @staticmethod
    def update_assessment_emails(assessment_name, new_emails):
        assessment_doc = QuestionDB.get_assessment(assessment_name)
        if assessment_doc:
            existing_emails = assessment_doc.get('assessment_email', [])
            updated_emails = list(set(existing_emails) | set(new_emails))
            assessment_collection.update_one(
                {"assessment_name": assessment_name},
                {"$set": {"assessment_email": updated_emails}}
            )
            return True
        return False

    @staticmethod
    def get_scheduled_count():
        # Query to find documents with status 'scheduled'
        query = {
            "status": "scheduled"
        }
        return assessment_collection.count_documents(query)

    @staticmethod
    def get_unscheduled_count():
        # Query to find documents where status is not 'scheduled'
        query = {
            "status": {"$ne": "scheduled"}
        }
        return assessment_collection.count_documents(query)
    @staticmethod
    def schedule_assessment_in_db(assessment_name, scheduled_time):
        query = {"assessment_name": assessment_name}
        new_values = {
            "$set": {
                "status": "scheduled",
                "schedule.scheduled_time": scheduled_time,
                "schedule_status": "scheduled",
                "schedule.initialized": 1,
                "updated_at": datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            }
        }
        assessment_collection.update_one(query, new_values)
    @staticmethod
    def update_assessment_status():
        """
        Function to check and update the status of assessments whose scheduled time has passed.
        It updates the status to 'ended' if the assessment's scheduled time is less than the current time.
        """
        try:
            # Connect to your MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            db = client['assessment_db']
            assessment_collection = db['assessments']

            # Get current time
            current_time = datetime.now()

            # Query to find assessments where 'status' is 'scheduled' and scheduled time is less than current time
            query = {
                "status": "scheduled",
                "schedule.scheduled_time": {"$lt": current_time}  # Check if scheduled_time is less than current time
            }

            # Values to update
            new_values = {
                "$set": {
                    "status": "ended",
                    "updated_at": current_time.strftime('%d-%m-%Y %H:%M:%S')
                }
            }

            # Update the assessments
            result = assessment_collection.update_many(query, new_values)

            # Check if any documents were modified
            if result.matched_count > 0:
                print(f"{result.modified_count} assessments updated to 'ended'")
            else:
                print("No assessments to update")

        except Exception as e:
            print(f"Error in updating assessments: {str(e)}")

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
    def store_image(profile_image):
        """Store the profile image in GridFS and return the file ID."""
        print("image iruuku")
        if profile_image:
            print("image ila")
            image_id = fs.put(profile_image.read(), 
                              filename=profile_image.name, 
                              content_type=profile_image.content_type)
            return str(image_id)  # Return as a string for easy storage in MongoDB
        return None

  
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
    
    @staticmethod
    def delete_candidate_by_email(email):
        result = users_collection.delete_one({'email': email})
        return result.deleted_count > 0

    
    @staticmethod
    def get_image(image_id):
        """Retrieve the image from GridFS using the image_id and return a base64 string."""
        if image_id:
            object_id = ObjectId(image_id)  # Convert string image_id to ObjectId
            grid_out = fs.find_one({"_id": object_id})  # Retrieve the image object
            if grid_out:
                image_data = grid_out.read()  # Read the binary data of the image
                # Convert the binary data to a base64 string
                return f"data:{grid_out.content_type};base64,{base64.b64encode(image_data).decode()}"
        return None

    @staticmethod
    def get_all_candidates():
        """Retrieve all candidates from the collection with their images."""
        candidates = list(users_collection.find())
        for candidate in candidates:
            # Retrieve the image object from GridFS
            image = Candidate.get_image(candidate.get('profile_image_id'))
            # Attach the image object directly to the candidate dictionary
            candidate['profile_image'] = image
            print(image)
        return candidates

    @staticmethod
    def get_count():
        return users_collection.count_documents({})


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
    
    @staticmethod
    def delete_instructor_by_email(email):
        result = instructors_collection.delete_one({'email': email})
        return result.deleted_count > 0
    
    @staticmethod
    def get_count():
        return instructors_collection.count_documents({})