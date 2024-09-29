from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from dotenv import load_dotenv
import openai
import os

from .models import Admin, Candidate, Instructor, QuestionDB
from main.forms import ContactForm
from main.candidate_form import SignupForm

# Candidate Views



from django.shortcuts import render

from .models import FeedbackModel 

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

        # Insert into MongoDB using the FeedbackModel
        FeedbackModel.insert_feedback(feedback_data)

        # Show success message and redirect or return a response
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback')  # Assuming 'feedback' is the name of the feedback page's URL

    # Render the form on GET request
    return render(request, 'main/Main_contact_us.html')




def index(request):
    return render(request, 'main/index.html')

def features(request):
    return render(request, 'main/features.html')

def forgotpassword(request):
    return render(request, 'main/forgotpass.html')

def candidate_login(request):
    return render(request, 'candidate/Candidate_login.html')

def candidate_dashboard(request):
    return render(request, 'candidate/Candidate_dashboard.html')

def candidate_preassesment(request):
    return render(request, 'candidate/Candidate_preassesment.html')

def system_check(request):
    if request.method == 'POST':
        # Here, you can add logic to check system requirements, such as:
        internet_check = request.is_ajax() and request.META.get('HTTP_REFERER') is not None
        camera_check = True  # This can be True since we can't check directly on server
        microphone_check = True  # This can also be True for the same reason

        # Prepare feedback for the user
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

def candidate_registration(request):
    return render(request, 'candidate/Candidate_registration.html')

def candidate_access(request):
    return render(request, 'candidate/Candidate_access.html')

def candidate_assesment(request):
    return render(request, 'candidate/Candidate_assesment.html')

def contact_us(request):
    return render(request, 'main/Main_contact_us.html')
#Instructor views
def instructor_login(request):
    if request.session.get('instructor_email'):
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the instructor exists
        instructor = Instructor.verify_instructor_login(email,password)

        if instructor:
            # If instructor exists, verify the password
            if Instructor.verify_instructor_login(email, password):
                request.session['instructor_email'] = email

                return redirect('instructor_dashboard')
            else:
                messages.error(request, 'Invalid password. Please try again.')
        else:
            messages.error(request, 'User does not exist. Please check your email.')

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
            "password": password,
            "status": 'deactive',
        }

        Instructor.add_instructor(instructor_data)
        messages.success(request, 'Instructor account created successfully!')
        return redirect('instructor_login')

    return render(request, 'instructor/Instructor_registration.html')

def instructor_dashboard(request):
    return render(request,'instructor/Instructor_dashboard.html')
def instructor_schedule(request):
    return render(request,'instructor/Instructor_schedule.html')


def instructor_usermanagement(request):
    can = Candidate.get_all_candidates()
    return render(request,'instructor/Instructor_usermanagement.html',{'candidates':can})

def instructor_create_assessment(request):
    return render(request,'instructor/Instructor_create_assessment.html')
def instructor_review_submission(request):
    return render(request,'instructor/Instructor_review_submission.html')
def instructor_report(request):
    return render(request,'instructor/Instructor_report.html')
def instructor_settings(request):
    return render(request,'instructor/Instructor_settings.html')



# Admin views
def admindashboard(request):
    return render(request, 'admin/Admin_dashboard.html')

def aiproctor(request):
    return render(request, 'admin/Admin_aiproctor.html')

def assessment(request):
    return render(request, 'admin/Admin_assessment.html')


from django.http import JsonResponse
from django.shortcuts import render
import json


from django.http import JsonResponse
from django.shortcuts import render
import json

import json
from django.shortcuts import render
from .models import QuestionDB  # Make sure to import your QuestionDB model

import json
from django.shortcuts import render
from .models import QuestionDB  # Make sure to import your QuestionDB model or service


from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
import openai
import os

from .models import Admin, Candidate, Instructor
from main.forms import ContactForm
from main.candidate_form import SignupForm

# Candidate Views

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
import smtplib
import json
# Store OTP temporarily for verification
otp_storage = {}

load_dotenv()
host_email = os.getenv("EMAIL_HOST_USER")
email_password = os.getenv("EMAIL_HOST_PASSWORD")
def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data['email']
        role = data['role']
    
        # Generate OTP
        otp = random.randint(100000, 999999)
        otp_storage[email] = otp  # Store OTP for verification

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
        if email in otp_storage and otp_storage[email] == int(entered_otp):
            del otp_storage[email]  # Clear OTP after successful verification
            return JsonResponse({'message': 'OTP verified'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)

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

def manualquestionupload(request):
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
    return render(request, 'admin/Admin_report.html')

def settings(request):
    return render(request, 'admin/Admin_settings.html')

def usermanagement(request):
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
            # Successful login, redirect to the admin dashboard
            return redirect('admindashboard')
        
        else:
            messages.error(request, 'Invalid Admin ID or Password')
            return render(request, 'admin/Admin_login.html')
    else:
        return render(request, 'admin/Admin_login.html')

def chatbot_view(request):
    return render(request, 'main/chatbot.html')



def candidate_login(request):
    if request.session.get('candidate_email'):
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        candidate = Candidate.verify_candidate_login(email, password)

        if candidate:
            request.session['candidate_email'] = candidate['email']
            return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'candidate/Candidate_login.html')


def candidate_registration(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Candidate.find_candidate_by_email(email):
                messages.error(request, 'Email already registered.')
                return redirect('candidate_login')

            candidate_data = {
                "first_name": form.cleaned_data['first_name'],
                "last_name": form.cleaned_data['last_name'],
                'dob': datetime.strptime(request.POST.get('dob'), '%Y-%m-%d'),
                "gender": form.cleaned_data['gender'],
                "mobile": form.cleaned_data['mobile'],
                "email": email,
                "address": form.cleaned_data['address'],
                "state": form.cleaned_data['state'],
                "country": form.cleaned_data['country'],
                "pincode": form.cleaned_data['pincode'],
                "qualification": form.cleaned_data['qualification'],
                "institution": form.cleaned_data['institution'],
                "password": form.cleaned_data['password'],
            }

            Candidate.add_candidate(candidate_data)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('candidate_login')
    else:
        form = SignupForm()

    return render(request, 'candidate/Candidate_registration.html', {'form': form})


def candidate_dashboard(request):
    if 'candidate_email' not in request.session:
        return redirect('candidate_login')
    return render(request, 'candidate/Candidate_dashboard.html')


def candidate_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('candidate_login')

def canididate_assessment_choice(request):
    return render(request, 'candidate/Candidate_assessment_choice.html')

def candidate_coding_test(request):
    return render(request, 'candidate/Candidate_coding_test.html')


# Instructor Views

def instructor_login(request):
    if request.session.get('instructor_email'):
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the instructor exists
        instructor = Instructor.verify_instructor_login(email,password)

        if instructor:
            # If instructor exists, verify the password
            if Instructor.verify_instructor_login(email, password):
                request.session['instructor_email'] = email

                return redirect('instructor_dashboard')
            else:
                messages.error(request, 'Invalid password. Please try again.')
        else:
            messages.error(request, 'User does not exist. Please check your email.')

    return render(request, 'instructor/Instructor_login.html')

def instructor_registration(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employeeId')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if Instructor.find_instructor_by_email(email):
            messages.error(request, 'Email is already registered.')
            return redirect('instructor_registration')

        instructor_data = {
            "employee_id": employee_id,
            "name": name,
            "email": email,
            "password": password,
            "status": 'deactive',
        }

        Instructor.add_instructor(instructor_data)
        messages.success(request, 'Instructor account created successfully!')
        return redirect('instructor_login')

    return render(request, 'instructor/Instructor_registration.html')


def instructor_dashboard(request):
    if 'instructor_email' not in request.session:
        return redirect('instructor_login')
    return render(request, 'instructor/Instructor_dashboard.html')


def instructor_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('instructor_login')


# Contact Form & Auto-Reply View
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            auto_reply = generate_auto_reply(message)

            send_mail(
                'Re: Your Contact Form Submission',
                auto_reply,
                'your_email@example.com',
                [email],
                fail_silently=False,
            )

            return HttpResponse('Thank you for your message. An auto-reply has been sent to your email.')
    else:
        form = ContactForm()

    return render(request, 'main/Main_contact_us.html', {'form': form})


# Chatbot View
def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = response.choices[0].message['content']
                return JsonResponse({'response': bot_reply})
            except Exception as e:
                return JsonResponse({'response': 'Unexpected error occurred.'}, status=500)
        else:
            return JsonResponse({'response': 'No message provided.'}, status=400)

    return JsonResponse({'response': 'Invalid request method.'}, status=405)


# Generate Auto-Reply for Contact Us
def generate_auto_reply(message):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message['content']
