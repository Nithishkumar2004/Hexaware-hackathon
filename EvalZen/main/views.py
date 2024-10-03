from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from dotenv import load_dotenv
import openai
import os
from .models import Admin, Candidate, Instructor, QuestionDB
from .forms import ContactForm
from .forms import SignupForm
import os
import json
import random
import smtplib
import time
from django.http import JsonResponse
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
import json

from django.contrib import messages
from django.shortcuts import redirect


from django.http import JsonResponse
from django.shortcuts import render
import json

import json
from django.shortcuts import render
from .models import QuestionDB  # Make sure to import your QuestionDB model

import json
from django.shortcuts import render
from .models import QuestionDB  # Make sure to import your QuestionDB model or service
from django.contrib.auth.hashers import make_password


from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
import openai
import os

from .models import Admin, Candidate, Instructor
from .forms import ContactForm
from .forms import SignupForm

# Candidate Views

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
import smtplib
import json

from .models import FeedbackModel 


# Store OTP and its timestamp for verification
otp_storage = {}

load_dotenv()
host_email = os.getenv("EMAIL_HOST_USER")
email_password = os.getenv("EMAIL_HOST_PASSWORD")


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
            "status": 'deactive',
        }

        Instructor.add_instructor(instructor_data)
        messages.success(request, 'Instructor account created successfully!')
        return redirect('instructor_login')

    return render(request, 'instructor/Instructor_registration.html')

def instructor_schedule(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
    return render(request,'instructor/Instructor_schedule.html')

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
    can = Candidate.get_all_candidates()
    return render(request,'instructor/Instructor_usermanagement.html',{'candidates':can})

def instructor_create_assessment(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
    return render(request,'instructor/Instructor_create_assessment.html')
def instructor_review_submission(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
    return render(request,'instructor/Instructor_review_submission.html')
def instructor_report(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
    return render(request,'instructor/Instructor_report.html')
def instructor_settings(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
    return render(request,'instructor/Instructor_settings.html')

def candidate_registration(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if the candidate already exists
            if Candidate.find_candidate_by_email(email):
                messages.error(request, 'Email already registered.')
                return redirect('candidate_login')

            # Prepare candidate data using request.POST directly
            candidate_data = {
                "first_name": form.cleaned_data['first_name'],
                "last_name": form.cleaned_data['last_name'],
                "dob": request.POST.get('dob'),  # Get dob directly from request.POST
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
                "status": "deactivated"  # Set initial status as 'deactive'
            }

            # Add candidate to the database
            Candidate.add_candidate(candidate_data)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('candidate_login')
    else:
        form = SignupForm()

    return render(request, 'candidate/Candidate_registration.html', {'form': form})

from django.http import JsonResponse
import json

def change_account_status(request):
    if request.method == 'POST':
     
        data = json.loads(request.body)
        email = data.get('email')
        new_status = data.get('status')
        user_type = data.get('userType')  # Get user type from the request
        print(f"Received request for {user_type} with email {email} and status {new_status}")


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
        return redirect('candidate_login')
    return render(request, 'candidate/Candidate_dashboard.html')

def candidate_preassesment(request):
    if 'candidate_email' not in request.session:
        return redirect('candidate_login')
    return render(request, 'candidate/Candidate_preassesment.html')

def system_check(request):
    if 'candidate_email' not in request.session:
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
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_access.html')

def candidate_assesment(request):
    # Check if the candidate is logged in
    if 'candidate_email' not in request.session:
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_assesment.html')


def canididate_assessment_choice(request):
    if 'candidate_email' not in request.session:
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_assessment_choice.html')

def candidate_coding_test(request):
    if 'candidate_email' not in request.session:
        return redirect('candidate_login')  # Redirect to the login page
    return render(request, 'candidate/Candidate_coding_test.html')

def candidate_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('candidate_login')


# Admin views
from django.shortcuts import render, redirect
from django.contrib import messages
import json

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
    return render(request, 'admin/Admin_assessment.html')

def manualquestionupload(request):
    # Check if the admin is logged in
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')  # Redirect to the login page

    question_db = QuestionDB()  # Create an instance of QuestionDB

    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)

            # Extract assessment number, MCQ list, and coding list from the data
            assessment_no = body_data.get('assessment_no')
            mcq_list = body_data.get('mcq', [])
            coding_list = body_data.get('coding', [])

            # Insert MCQs if available
            if mcq_list:
                mcq_result = question_db.insert_mcq(assessment_no, mcq_list)

            if coding_list:
                coding_result = question_db.insert_coding_question(assessment_no, coding_list)

            # On successful upload, render a success message
            return render(request, 'admin/Admin_manualquestionupload.html', {'success': 'Questions uploaded successfully!'})

        except json.JSONDecodeError:
            return render(request, 'admin/Admin_manualquestionupload.html', {'error': 'Invalid JSON data. Please ensure your request contains valid JSON.'})
        except Exception as e:
            return render(request, 'admin/Admin_manualquestionupload.html', {'error': str(e)})

    # For GET requests or other methods, return the form page (if needed)
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

from django.shortcuts import redirect
from django.contrib.auth import logout

def admin_logout(request):
    # Log out the user by clearing the session and logging them out
    logout(request)  # This function clears the session and logs out the user
    
    # Redirect to the admin login page after logging out
    return redirect('admin_login')  # Ensure 'admin_login' is the name of the login page URL pattern


