from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from main.forms import ContactForm
from main.candidate_form import SignupForm
import openai
import os
from dotenv import load_dotenv
import pymongo
from pymongo.mongo_client import MongoClient
from django.contrib import messages  # Import messages for displaying alerts
from django.shortcuts import redirect
from pymongo.server_api import ServerApi
from django.contrib import messages  # Make sure to import messages

from django.shortcuts import redirect, render
from django.contrib import messages



# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')  # Make sure MONGO_URI is defined in your .env file


client = pymongo.MongoClient(MONGO_URI,server_api=ServerApi('1'))

#database
db = client['users'] 

#collections
users_collection = db['candidate'] 
instructors_collection = db['instructors']


client.admin.command('ping')
   
def index(request):
    return render(request, 'main/index.html')

def candidate_login(request):
    return render(request, 'candidate/Candidate_login.html')

def candidate_dashboard(request):
    return render(request, 'candidate/Candidate_dashboard.html')

def candidate_preassesment(request):
    return render(request, 'candidate/Candidate_preassesment.html')

def candidate_registration(request):
    return render(request, 'candidate/Candidate_registration.html')



def candidate_assesment(request):
    return render(request, 'candidate/Candidate_assesment.html')

def contact_us(request):
    return render(request, 'main/Main_contact_us.html')
#Instructor views

def instructor_login(request):
    return render(request, 'instructor/Instructor_login.html')

def instructor_registration(request):
    return render(request,'instructor/Instructor_registration.html')
def instructor_dashboard(request):
    return render(request,'instructor/Instructor_dashboard.html')
def instructor_schedule(request):
    return render(request,'instructor/Instructor_schedule.html')
def instructor_usermanagement(request):
    return render(request,'instructor/Instructor_usermanagement.html')
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

def manualquestionupload(request):
    return render(request, 'admin/Admin_manualquestionupload.html')

def report(request):
    return render(request, 'admin/Admin_report.html')

def settings(request):
    return render(request, 'admin/Admin_settings.html')

def usermanagement(request):
    return render(request, 'admin/Admin_usermanagement.html')

def adminlogin(request):
    return render(request, 'admin/Admin_login.html')
def chatbot_view(request):
    return render(request, 'main/chatbot.html')

def generate_auto_reply(message):
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message['content']

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Generate auto-reply using OpenAI
            auto_reply = generate_auto_reply(message)

            # Send auto-reply email
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

def instructor_registration(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employeeId')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if email is already registered
        existing_instructor = instructors_collection.find_one({"email": email})
        if existing_instructor:
            messages.error(request, 'Email is already registered. Please use a different email.')
            return redirect('Instructor_registration')  # Redirect back to registration

        # Save instructor data to MongoDB
        instructor_data = {
            "employee_id": employee_id,
            "name": name,
            "email": email,
            "password": password,  

            "status":'deactive',
            #initial status deacitve
            
            # You might want to hash the password before storing it
        }

        instructors_collection.insert_one(instructor_data)

        messages.success(request, 'Instructor account created successfully!')
        return redirect('Instructor_login')  # Redirect to login page after successful registration

    return render(request, 'instructor/Instructor_registration.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages

def candidate_registration(request):
    # Check if the request method is POST
    if request.method == 'POST':
        print("Form Submitted: ", request.POST)  # Debug line to see form data

        form = SignupForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug line
            email = form.cleaned_data['email']

            # Check if the email already exists in MongoDB
            existing_candidate = users_collection.find_one({"email": email})
            if existing_candidate:
                messages.error(request, 'Email is already registered. Please log in or use a different email.')
                return redirect('candidate_login')  # Redirect to login page if email exists

            # Prepare candidate data
            candidate_data = {
                "first_name": form.cleaned_data['first_name'],
                "last_name": form.cleaned_data['last_name'],
                'dob': datetime.strptime(request.POST.get('dob'), '%Y-%m-%d'),  # Convert to datetime
                "gender": form.cleaned_data['gender'],
                "mobile": form.cleaned_data['mobile'],
                "email": email,
                "address": form.cleaned_data['address'],
                "state": form.cleaned_data['state'],
                "country": form.cleaned_data['country'],
                "pincode": form.cleaned_data['pincode'],
                "qualification": form.cleaned_data['qualification'],
                "institution": form.cleaned_data['institution'],
                "password": form.cleaned_data['password'],  # Consider hashing this
            }

            # Insert candidate data into MongoDB
            users_collection.insert_one(candidate_data)

            # Set a success message and redirect to login page
            messages.success(request, 'Registration Successful! Please log in.')
            return redirect('candidate_login')  # Redirect to login after successful registration
        else:
            print("Form is not valid")  # Debug line
    else:
        form = SignupForm()  # Initialize the form for GET requests

    return render(request, 'candidate/Candidate_registration.html', {'form': form})  # Render registration page with form


def candidate_login(request):
    # Check if the user is already logged in
    if request.session.get('candidate_email'):
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Query MongoDB to find the user by email
        candidate = users_collection.find_one({"email": email})

        if candidate:
            # Check if the entered password matches the stored password
            if candidate['password'] == password:
                # Store user information in session
                request.session['candidate_email'] = candidate['email']
                
                # Redirect to candidate dashboard
                return redirect('candidate_dashboard')
            else:
                # Password is incorrect, display an error message
                messages.error(request, 'Incorrect password. Please try again.')
        else:
            # User with the provided email does not exist
            messages.error(request, 'User does not exist. Please check your email or sign up.')

    return render(request, 'candidate/Candidate_login.html')


# Logout View
def candidate_logout(request):
    # Clear the session data
    request.session.flush()  # This clears all session data, effectively logging the user out

    # Redirect to login page
    messages.success(request, 'You have been logged out successfully.')
    return redirect('candidate_login')


# Dashboard View
def candidate_dashboard(request):
    # Check if candidate is logged in by looking for the session data
    if 'candidate_email' not in request.session:
        # If no session, redirect to login page
        return redirect('candidate_login')

    # Proceed with dashboard logic if logged in
    return render(request, 'candidate/Candidate_dashboard.html')

def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')

        if user_message:
            openai.api_key = OPENAI_API_KEY
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                print(response)
                bot_reply = response.choices[0].message['content']
                return JsonResponse({'response': bot_reply})
            
            except Exception as e:
                
                return JsonResponse({'response': 'Unexpected error occurred.'}, status=500)
        else:
            return JsonResponse({'response': 'No message provided.'}, status=400)

    return JsonResponse({'response': 'Invalid request method.'}, status=405)

