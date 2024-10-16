from datetime import datetime, timedelta, timezone
from email import errors
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

class MongoDBConnection:
    @staticmethod
    def check_connection():
        try:
            # Establish MongoDB connection
            client = pymongo.MongoClient(MONGO_URI)
            # Ping the MongoDB server
            client.admin.command('ping')
            return "Stable"
        except errors.ConnectionFailure:
            return "Unstable - Connection Failure"
        except Exception as e:
            return f"Unstable - Error: {str(e)}"
        finally:
            client.close()  # Ensure client is closed after check
class QuestionDB:
    
    @staticmethod
    def generate_assessment_id():
        current_year = datetime.now().year
        existing_assessments = assessment_collection.find()
        count = len(list(existing_assessments))
        new_id = f"Evalzen-{count + 1}"
        return new_id

    def delete_assessment(assessment_id):
        return assessment_collection.delete_one({'assessment_name': assessment_id})

    @staticmethod
    def insert_assessment(data):
        return assessment_collection.insert_one(data)

    @staticmethod
    def get_all_schedule_assessment():
        return list(assessment_collection.find({'status': 'scheduled'}))



    @staticmethod
    def get_invited_assessments(email):
        query = {
            "candidates": email
        }
        invited_assessments = list(assessment_collection.find(query))
        return invited_assessments



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
    def get_assessment_count(status):
        query = {"status": status}
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
        # Get current UTC time and convert to IST
        current_utc_time = datetime.now(timezone.utc)
        ist_time = current_utc_time + timedelta(hours=5, minutes=30)

        # Format current IST time for comparison
        current_datetime = ist_time.strftime("%Y-%m-%d %H:%M")
        current_datetime = datetime.strptime(current_datetime, '%Y-%m-%d %H:%M')

        assessments = QuestionDB.get_all_schedule_assessment()
        for assessment in assessments:
            schedule_date_str = assessment['schedule']['date']
            schedule_time_str = assessment['schedule']['time']
            duration = int(assessment['schedule'].get('duration', 0))

            # Combine date and time
            scheduled_datetime_str = f"{schedule_date_str} {schedule_time_str}"
            scheduled_datetime = datetime.strptime(scheduled_datetime_str, '%Y-%m-%d %H:%M')

            # Calculate end time
            end_time = scheduled_datetime + timedelta(minutes=duration)

            # Check assessment status
            if scheduled_datetime > current_datetime:
                new_status = 'scheduled'
            elif scheduled_datetime <= current_datetime < end_time:
                new_status = 'active'
            else:
                new_status = 'ended'
            
            # Update the assessment status in the database
            query = {"_id": assessment['_id']}
            new_values = {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                }
            }
            assessment_collection.update_one(query, new_values)
    @staticmethod
    def fetch_Assessment(assessment_name, candidate_email):
        if not isinstance(assessment_name, str) or not isinstance(candidate_email, str):
            print("Error: Both assessment_name and candidate_email should be strings.")
            return None

        query = {"assessment_id": assessment_name, "candidates": candidate_email}
        assessment = assessment_collection.find_one(query)
        
        if assessment:
            print("Assessment found:", assessment)
        else:
            return False

        return assessment


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
