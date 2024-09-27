from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
import openai
import os

from .models import Candidate, Instructor
from main.forms import ContactForm
from main.candidate_form import SignupForm

# Candidate Views



from django.shortcuts import render

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

def manualquestionupload(request):
    return render(request, 'admin/Admin_manualquestionupload.html')

def report(request):
    return render(request, 'admin/Admin_report.html')

def settings(request):
    return render(request, 'admin/Admin_settings.html')

def usermanagement(request):
    candidates = Candidate.get_all_candidates()  # Assuming this method returns a queryset of candidates
    instructors = Instructor.get_all_instructors()  # Ensure to call the method with parentheses
  
    return render(request, 'admin/Admin_usermanagement.html', {'candidates': candidates, 'instructors': instructors})

def adminlogin(request):
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
