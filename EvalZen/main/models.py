from datetime import datetime, timedelta
import os
from bson import ObjectId
from dotenv import load_dotenv
import gridfs
import pymongo
from pymongo.server_api import ServerApi
from django.contrib.auth.hashers import check_password, make_password
import base64

# Load environment variables from .env file
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')

if MONGO_URI is None:
    raise ValueError("MONGO_URI environment variable is not set.")

client = pymongo.MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Database
db = client['users']
users_collection = db['candidate']
instructors_collection = db['instructors']

fs = gridfs.GridFS(db)

questions_db = client['Questions']
assessment_collection = questions_db['Assessment']

admin_db = client['AdminAuth']
admin_collection = admin_db['Admin Details']

feedback_db = client['Feedback']
collection = feedback_db['Details']

class QuestionDB:
    
    @staticmethod
    def delete_assessment(assessment_id):
        return assessment_collection.delete_one({'assessment_name': assessment_id})

    @staticmethod
    def insert_assessment(data):
        return assessment_collection.insert_one(data)

    @staticmethod
    def get_all_schedule_assessment():
        return list(assessment_collection.find({'status': 'scheduled'}))
    

    @staticmethod
    def get_all_assessment():
        return list(assessment_collection.find())

    @staticmethod
    def update_assessment_emails(assessment_name, new_emails):
        assessment_doc = assessment_collection.find_one({"assessment_name": assessment_name})
        
        if assessment_doc:
            existing_emails = assessment_doc.get('candidates', [])
            updated_emails = list(set(existing_emails) | set(new_emails))
            assessment_collection.update_one(
                {"assessment_name": assessment_name},
                {"$set": {"candidates": updated_emails}}
            )
            return True
        return False

    @staticmethod
    def get_scheduled_count():
        query = {"status": "scheduled"}
        return assessment_collection.count_documents(query)

    @staticmethod
    def get_unscheduled_count():
        query = {"status": {"$ne": "scheduled"}}
        return assessment_collection.count_documents(query)

    @staticmethod
    def schedule_assessment_in_db(assessment_name, assessment_date,assessment_time,time_period):
        query = {"assessment_name": assessment_name}
        new_values = {
            "$set": {
                "status": "scheduled",
                "schedule.date": assessment_date,
                "schedule.duration": time_period,
                "schedule.time": assessment_time,
                "updated_at": datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            }
        }
        assessment_collection.update_one(query, new_values)


    @staticmethod
    def update_assessment_statuses():
        current_time = datetime.now()

        # Fetch all scheduled assessments
        assessments = QuestionDB.get_all_schedule_assessment()

        for assessment in assessments:
            scheduled_time_str = assessment['schedule']['scheduled_time']
            duration = assessment['schedule']['duration']  # Assuming duration is stored in minutes
            
            # Convert scheduled_time to a datetime object
            if isinstance(scheduled_time_str, str):
                scheduled_datetime = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")
            else:
                scheduled_datetime = scheduled_time_str

            if current_time < scheduled_datetime:
                # Assessment is upcoming
                new_status = 'scheduled'
            else:
                # Assessment is active or ended
                print(duration)
                if duration:
                    duration_timedelta = timedelta(minutes=duration)
                    duration_end_time = scheduled_datetime + duration_timedelta
                    
                    if scheduled_datetime <= current_time < duration_end_time:
                        new_status = 'active'
                    else:
                        new_status = 'ended'
                else:
                    new_status = 'ended'  # No duration specified, mark as ended

            # Update the status in the database
            query = {"_id": assessment['_id']}
            new_values = {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                }
            }
            assessment_collection.update_one(query, new_values)

class Admin:
    @staticmethod
    def get_admin_credentials(admin_id):
        return admin_collection.find_one({"admin_id": admin_id})

class FeedbackModel:
    @staticmethod
    def insert_feedback(data):
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
        if profile_image:
            image_id = fs.put(profile_image.read(), 
                              filename=profile_image.name, 
                              content_type=profile_image.content_type)
            return str(image_id) 
        return None

    @staticmethod
    def verify_candidate_login(email, password):
        candidate = users_collection.find_one({"email": email})

        if candidate is None:
            return None  # Candidate not found

        status = candidate.get('status')
        if status == "deactivated":
            return "not activated, please contact instructor"
        
        is_correct = check_password(password, candidate['password'])

        if is_correct:
            return candidate

        return None

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
        return result.modified_count > 0
    
    @staticmethod
    def delete_candidate_by_email(email):
        result = users_collection.delete_one({'email': email})
        return result.deleted_count > 0

    @staticmethod
    def get_image(image_id):
        if image_id:
            object_id = ObjectId(image_id)
            grid_out = fs.find_one({"_id": object_id})
            if grid_out:
                image_data = grid_out.read()
                return f"data:{grid_out.content_type};base64,{base64.b64encode(image_data).decode()}"
        return None

    @staticmethod
    def get_all_candidates():
        candidates = list(users_collection.find())
        for candidate in candidates:
            image = Candidate.get_image(candidate.get('profile_image_id'))
            candidate['profile_image'] = image
        return candidates

    @staticmethod
    def get_count():
        return users_collection.count_documents({})

class Instructor:
    @staticmethod
    def update_status(email, new_status):
        result = instructors_collection.update_one(
            {'email': email},
            {'$set': {'status': new_status}}
        )
        return result.modified_count > 0

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

        if instructor:
            if check_password(password, instructor['password']):
                if instructor['status'] == 'activated':
                    return instructor
                else:
                    return "Account created but not activated. Please contact admin."
        
        return False

    @staticmethod
    def get_all_instructors():
        instructors = list(instructors_collection.find())
        return instructors
    
    @staticmethod
    def delete_instructor_by_email(email):
        result = instructors_collection.delete_one({'email': email})
        return result.deleted_count > 0
    
    @staticmethod
    def get_count():
        return instructors_collection.count_documents({})
