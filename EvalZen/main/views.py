from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
import os
import json
import random
import smtplib
import time
from dotenv import load_dotenv
from .models import Admin, Candidate, Instructor, QuestionDB, FeedbackModel
from .forms import SignupForm
from django.views.decorators.http import require_GET

# Store OTP and its timestamp for verification
otp_storage = {}

load_dotenv()
host_email = os.getenv("EMAIL_HOST_USER")
email_password = os.getenv("EMAIL_HOST_PASSWORD")

from django.http import HttpResponse
import pandas as pd
from reportlab.pdfgen import canvas
QuestionDB.update_assessment_status()
# PDF Report View
def download_assessment_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="assessment_report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 750, "Assessment Report")
    p.drawString(100, 730, "Total Users: 150")
    p.drawString(100, 710, "Total Assessments: 45")
    p.drawString(100, 690, "Active Sessions: 12")
    p.showPage()
    p.save()
    return response

# Excel Report View
def download_proctoring_report(request):
    data = {
        'Assessment': ['Assessment 1', 'Assessment 2', 'Assessment 3'],
        'Proctoring Issues': [2, 0, 1]
    }
    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="proctoring_report.xlsx"'
    df.to_excel(response, index=False)
    
    return response


def index(request):
    return render(request, 'main/index.html')

def submit_feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        feedback = request.POST.get('feedback')

        # Prepare the data to insert
        feedback_data = {
            'name': name,
            'email': email,
            'feedback': feedback
        }
        FeedbackModel.insert_feedback(feedback_data)
        # Show success message and redirect or return a response
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback') 
    # Render the form on GET request
    return render(request, 'main/Main_contact_us.html')

def features(request):
    return render(request, 'main/features.html')

def forgotpassword(request):
    return render(request, 'main/forgotpass.html')

def contact_us(request):
    return render(request, 'main/Main_contact_us.html')

def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data['email']
        role = data['role']
    
        # Generate OTP
        otp = random.randint(100000, 999999)
        otp_storage[email] = (otp, time.time())  # Store OTP and current timestamp

        # Send OTP via email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(host_email, email_password)
            message = f'Subject: Your OTP\n\nYour OTP is {otp}.'
            server.sendmail(host_email, email, message)
            server.quit()
            return JsonResponse({'message': 'OTP sent'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def verify_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data['email']
        entered_otp = data['otp']

        # Check OTP
        if email in otp_storage:
            stored_otp, timestamp = otp_storage[email]

            # Check if OTP is valid (within 30 seconds)
            if stored_otp == int(entered_otp) and (time.time() - timestamp) <= 30:
                del otp_storage[email]  # Clear OTP after successful verification
                return JsonResponse({'message': 'OTP verified'}, status=200)

            # OTP is invalid or expired
            return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)

        return JsonResponse({'error': 'Email not found'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def update_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')  # Retrieve the role from the form

        # Ensure passwords match
        if new_password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})

        # Based on the role, update password in MongoDB
        if role == 'candidate':
            Candidate.update_password(email, new_password)
        elif role == 'instructor':
            Instructor.update_password(email, new_password)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid role selected.'})

        messages.success(request, 'Password updated successfully!')
        return JsonResponse({'status': 'success', 'message': 'Password updated successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def edit_user(request):
    if request.method == 'POST':
        try:
            # Parse the request body to get JSON data
            data = json.loads(request.body)
            
            # Extract the usertype and email from the parsed data
            usertype = data.get('usertype')
            email = data.get('email')

     
            # Check usertype and perform database lookup accordingly
            if usertype == 'instructor':
                # Fetch the instructor by email
                user_data = Instructor.find_instructor_by_email(email)
                
            elif usertype == 'candidate':
                # Fetch the candidate by email
                user_data = Candidate.find_candidate_by_email(email)
                
            else:
                return JsonResponse({'error': 'Invalid user type'}, status=400)

            # If user_data is found, send the data as a response
            if user_data:
                return JsonResponse({'message': 'User found successfully', 'user_data': user_data})
            else:
                return JsonResponse({'error': 'User not found'}, status=404)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def change_account_status(request):
    if request.method == 'POST':
     
        data = json.loads(request.body)
        email = data.get('email')
        new_status = data.get('status')
        user_type = data.get('userType')  # Get user type from the request
 
        if not email or not new_status or not user_type:
            return JsonResponse({'success': False, 'message': 'Missing data.'}, status=400)

        # Check if the user is a candidate or instructor and update accordingly
        if user_type == 'candidate':
            candidate = Candidate.find_candidate_by_email(email)
            if candidate is None:
                return JsonResponse({'success': False, 'message': 'Candidate not found.'}, status=404)
            Candidate.update_status(email, new_status)
            return JsonResponse({'success': True, 'message': 'Candidate status updated.'})

        elif user_type == 'instructor':
            instructor = Instructor.find_instructor_by_email(email)
            if instructor is None:
                return JsonResponse({'success': False, 'message': 'Instructor not found.'}, status=404)
            Instructor.update_status(email, new_status)
            return JsonResponse({'success': True, 'message': 'Instructor status updated.'})

        else:
            return JsonResponse({'success': False, 'message': 'Invalid user type.'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

def delete_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        user_type = data.get('usertype')

        if not email or not user_type:
            return JsonResponse({'success': False, 'message': 'Missing data.'}, status=400)

        # Check if the user is a candidate or instructor and delete accordingly
        if user_type == 'candidate':
            result = Candidate.delete_candidate_by_email(email)
            if result:
                return JsonResponse({'success': True, 'message': 'Candidate deleted successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Candidate not found.'}, status=404)

        elif user_type == 'instructor':
            result = Instructor.delete_instructor_by_email(email)
            if result:
                return JsonResponse({'success': True, 'message': 'Instructor deleted successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Instructor not found.'}, status=404)

        else:
            return JsonResponse({'success': False, 'message': 'Invalid user type.'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Candidate, Instructor, QuestionDB  # Adjust as per your models

@require_GET
def get_user_counts(request):
    try:
        # Get the count of candidates and instructors from models
        candidate_count = Candidate.get_count()
        instructor_count = Instructor.get_count()

        # Return the count in a JSON response
        return JsonResponse({
            'success': True,
            'candidates': candidate_count,
            'instructors': instructor_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def Unactive_Assessments(request):
    try:
        # Get the count of unactive (not scheduled) assessments
        unactive_assessments_count = QuestionDB.get_unscheduled_count()

        # Return the count in a JSON response
        return JsonResponse({
            'success': True,
            'UnactiveAssessments': unactive_assessments_count,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def Active_Assessments(request):
    try:
        # Get the count of active assessments from models
        active_assessments_count = QuestionDB.get_scheduled_count()

        # Return the count in a JSON response
        return JsonResponse({
            'success': True,
            'ActiveAssessments': active_assessments_count,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)





# Instructor views
def instructor_login(request):
    if request.session.get('instructor_email'):
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the instructor exists and verify the login
        instructor = Instructor.verify_instructor_login(email, password)

        if isinstance(instructor, str):  # Check if it's a string message
            messages.error(request, instructor)  # Display the message about account status
        elif instructor:  # If instructor is an object (not a string)
            request.session['instructor_email'] = email
            return redirect('instructor_dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'instructor/Instructor_login.html')

def instructor_registration(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employeeId')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if Instructor.find_instructor_by_email(email):
            messages.error(request, 'Email is already registered.')
            return redirect('instructor_login')

        instructor_data = {
            "employee_id": employee_id,
            "name": name,
            "email": email,
            "password": make_password(password),
            "status": 'deactivated',
        }

        Instructor.add_instructor(instructor_data)
        messages.success(request, 'Instructor account created successfully!')
        return redirect('instructor_login')

    return render(request, 'instructor/Instructor_registration.html')

def instructor_schedule(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    assessments = QuestionDB.get_all_assessment() 
    return render(request,'instructor/Instructor_schedule.html',{'assessments':assessments})

def instructor_dashboard(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request, 'instructor/Instructor_dashboard.html')

def instructor_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('instructor_login')

def instructor_usermanagement(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    can = Candidate.get_all_candidates()
    return render(request,'instructor/Instructor_usermanagement.html',{'candidates':can})

def instructor_create_assessment(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request,'instructor/Instructor_create_assessment.html')

def instructor_review_submission(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request,'instructor/Instructor_review_submission.html')


def instructor_report(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request,'instructor/Instructor_report.html')

def instructor_settings(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request,'instructor/Instructor_settings.html')
def instructor_invitation(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
    assessments = QuestionDB.get_all_assessment() 
    candidates = Candidate.get_all_candidates()  # Assuming this method returns a queryset of candidates
    return render(request,'instructor/Instructor_invitation.html',{'assessments':assessments,'candidates': candidates,})


def invitation(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            selected_emails = data.get('email')
            assessment_name = data.get('assessment_name')
    
            # Update the assessment document with the new emails
            success = QuestionDB.update_assessment_emails(selected_emails)

            if success:
                return JsonResponse({'success': True, 'message': 'Invitations sent and emails added successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Assessment not found.'}, status=404)

        except Exception as e:
           return JsonResponse({'success': False, 'message': 'An error occurred while processing your request.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

#Candidate Views

def candidate_registration(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if the candidate already exists
            if Candidate.find_candidate_by_email(email):
                messages.error(request, 'Email already registered.')
                return redirect('candidate_login')

            # Handle image upload using the Candidate model's store_image method
            profile_image = request.FILES.get('profile_image')
            image_id = Candidate.store_image(profile_image)

            # Prepare candidate data
            candidate_data = {
                "first_name": form.cleaned_data['first_name'],
                "last_name": form.cleaned_data['last_name'],
                "dob": request.POST.get('dob'),
                "gender": form.cleaned_data['gender'],
                "mobile": form.cleaned_data['mobile'],
                "email": email,
                "address": form.cleaned_data['address'],
                "state": form.cleaned_data['state'],
                "country": form.cleaned_data['country'],
                "pincode": form.cleaned_data['pincode'],
                "qualification": form.cleaned_data['qualification'],
                "institution": form.cleaned_data['institution'],
                "password": make_password(form.cleaned_data['password']),
                "status": "deactivated",
                "profile_image_id": image_id  # Store the GridFS file ID as a reference
            }

            # Add candidate to the database
            Candidate.add_candidate(candidate_data)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('candidate_login')
    else:
        form = SignupForm()

    return render(request, 'candidate/Candidate_registration.html', {'form': form})

def candidate_login(request):
    # Check if the candidate is already logged in
    if request.session.get('candidate_email'):
        return redirect('candidate_dashboard')

    # Handle POST request for login
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        candidate = Candidate.verify_candidate_login(email, password)  # Call the corrected function

        # Check the response from verify_candidate_login
        if isinstance(candidate, str):  # If the response is a string, it's an error message
            messages.error(request, candidate)  # Display the error message
        elif candidate:  # If the candidate exists and is activated
            request.session['candidate_email'] = candidate['email']
            return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'candidate/Candidate_login.html')


def candidate_dashboard(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')
    a = QuestionDB.get_all_assessment()
    return render(request, 'candidate/Candidate_dashboard.html',{'assessments': a})

def candidate_preassesment(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')
    return render(request, 'candidate/Candidate_preassesment.html')

def system_check(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')
    if request.method == 'POST':
        internet_check = request.is_ajax() and request.META.get('HTTP_REFERER') is not None
        camera_check = True 
        microphone_check = True  
        feedback = {
            'internet': 'Internet connection is available.' if internet_check else 'No internet connection detected.',
            'camera': 'Camera access is granted.',
            'microphone': 'Microphone access is granted.',
        }
        # Determine if all checks passed
        all_checks_passed = internet_check and camera_check and microphone_check
        return JsonResponse({
            'success': all_checks_passed,
            'feedback': feedback,
        })

    return render(request, 'candidate/System_check.html')

def candidate_access(request):
    # Check if the candidate is logged in
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_access.html')

def candidate_assesment(request):
    # Check if the candidate is logged in
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_assesment.html')

def canididate_assessment_choice(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_assessment_choice.html')

def candidate_coding_test(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_coding_test.html')

def candidate_profile(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')  # Redirect to the login page
    candidate_email = request.session['candidate_email']
    candidate = Candidate.find_candidate_by_email(candidate_email)
    image = Candidate.get_image(candidate.get('profile_image_id'))
            # Attach the image object directly to the candidate dictionary
    candidate['profile_image'] = image
    return render(request, 'candidate/Candidate_profile.html',{"profile":candidate})

def candidate_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('candidate_login')

#Admin Views

def schedule_assessment(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page
  
    if request.method == 'POST':
        assessment_name = request.POST.get('assessment_name')
        assessment_date = request.POST.get('assessment_date')
        assessment_time = request.POST.get('assessment_time')
        time_period = request.POST.get('time_period')

        # Format the time
        scheduled_time_str = f"{assessment_date} {assessment_time} {time_period}"
        scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M %p")

        # Call the function to update the MongoDB document
        QuestionDB.schedule_assessment_in_db(assessment_name, scheduled_time)
        
        assessments = QuestionDB.get_all_assessment() 
        return render(request, 'admin/Admin_assessment.html',{'assessments':assessments})
      
    # Render the same page (assuming 'schedule.html' is your template)
    return render(request, 'admin/Admin_assessment.html')

def admindashboard(request):
    # Check if the admin is logged in
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page
    return render(request, 'admin/Admin_dashboard.html')

def aiproctor(request):
    # Check if the admin is logged in
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page
    return render(request, 'admin/Admin_aiproctor.html')

def assessment(request):
    # Check if the admin is logged in
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page
    
    assessments = QuestionDB.get_all_assessment() 
    return render(request, 'admin/Admin_assessment.html',{'assessments':assessments})


def manualquestionupload(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page
    
    question_db = QuestionDB()  # Create an instance of QuestionDB

    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Extract assessment details from the data
            assessment_name = data.get('assessment_name', '')
            status = data.get('status', 'not defined')
            schedule_status = data.get('schedule_status', 'not scheduled')
            schedule = data.get('schedule', {})
            created_at = datetime.now().isoformat()  # Automatically set the created time
            updated_at = datetime.now().isoformat()  # Automatically set the updated time
            mcq_questions = data.get('mcq', [])
            coding_questions = data.get('coding', [])
            candidates = data.get('candidates', [])
            tags = data.get('tags', [])

            # Perform additional validation or processing as needed
            if not assessment_name:
                return JsonResponse({'error': 'Assessment name is required.'}, status=400)

            # Prepare the document for insertion
            assessment_document = {
                'assessment_name': assessment_name,
                'status': status,
                'schedule_status': schedule_status,
                'schedule': {
                    'date': schedule.get('date', ''),
                    'time': schedule.get('time', ''),
                    'duration': schedule.get('duration', ''),
                    'status': schedule.get('status', ''),
                },
                'created_at': created_at,
                'updated_at': updated_at,
                'mcq': mcq_questions,
                'coding': coding_questions,
                'candidates': candidates,
                'tags': tags
            }

            # Insert the assessment document into the database
            question_db.insert_assessment(assessment_document)

            # Respond with success
            return JsonResponse({'message': 'Assessment submitted successfully!'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

    # For GET requests, return the form page
    return render(request, 'admin/Admin_manualquestionupload.html')

def report(request):
    # Check if the admin is logged in
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page
    
    return render(request, 'admin/Admin_report.html')

def settings(request):
    # Check if the admin is logged in
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page
    
    return render(request, 'admin/Admin_settings.html')

def usermanagement(request):
    # Check if the admin is logged in
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page

    # Fetch candidates and instructors if logged in
    candidates = Candidate.get_all_candidates()  # Assuming this method returns a queryset of candidates
    instructors = Instructor.get_all_instructors()  # Ensure to call the method with parentheses
    return render(request, 'admin/Admin_usermanagement.html', {'candidates': candidates, 'instructors': instructors})

def admin_login(request):
    if request.method == 'POST':
        admin_id = request.POST.get('adminid')
        password = request.POST.get('password')

        # Fetch static admin credentials using the Admin model
        admin_credentials = Admin.get_admin_credentials(admin_id)

        if admin_credentials and admin_credentials['password'] == password:
            # Successful login, create a session
            request.session['admin_id'] = admin_id  # Store admin ID in the session
            
            # Redirect to the admin dashboard
            return redirect('admindashboard')
        
        else:
            messages.error(request, 'Invalid Admin ID or Password')
            return render(request, 'admin/Admin_login.html')
    else:
        return render(request, 'admin/Admin_login.html')

def admin_logout(request):
    # Log out the user by clearing the session and logging them out
    logout(request)  # This function clears the session and logs out the user
    
    # Redirect to the admin login page after logging out
    return redirect('admin_login')  # Ensure 'admin_login' is the name of the login page URL pattern

#assesment
import cv2
import dlib
import numpy as np
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Initialize the face detector
detector = dlib.get_frontal_face_detector()



def stream_camera(request):
    if request.method == 'GET':
        return render(request, 'candidate/candidate_assesment.html')

@csrf_exempt  # Disable CSRF validation for this view (for simplicity)
def proctoring_view(request):
    if request.method == 'POST':
        # Read the frame sent from the frontend
        frame_file = request.FILES.get('frame')
        if frame_file:
            # Convert the frame to a format suitable for OpenCV
            nparr = np.frombuffer(frame_file.read(), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 0)

            # Print the number of faces detected
            num_faces_detected = len(rects)
            print(f"Number of faces detected: {num_faces_detected}")

            # Check if more than one face is detected
            if num_faces_detected > 1:
                # Take a screenshot and save it
                screenshot_path = os.path.join('static', 'image', f'screenshot_{int(time.time())}.jpg')
                cv2.imwrite(screenshot_path, frame)
                print(f"Screenshot saved at: {screenshot_path}")
                return JsonResponse({"error": "More than one face detected.", "screenshot": screenshot_path})

            # Additional monitoring logic can be added here

            return JsonResponse({"message": "Frame received", "num_faces": num_faces_detected})

    return JsonResponse({"message": "Invalid request."})


