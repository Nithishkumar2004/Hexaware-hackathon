from datetime import datetime
import os
import random
import smtplib
import time
import json
import cv2
import dlib
import numpy as np
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_GET
from urllib.parse import unquote
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from django.conf import settings
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

from .models import Admin, Candidate, Instructor, MongoDBConnection, QuestionDB, FeedbackModel
from .forms import SignupForm


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
        feedback_data = {'name': name, 'email': email, 'feedback': feedback}
        FeedbackModel.insert_feedback(feedback_data)
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback')
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
        otp = random.randint(100000, 999999)
        otp_storage[email] = (otp, time.time())
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
        if email in otp_storage:
            stored_otp, timestamp = otp_storage[email]
            if stored_otp == int(entered_otp) and (time.time() - timestamp) <= 30:
                del otp_storage[email]
                return JsonResponse({'message': 'OTP verified'}, status=200)
            return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)
        return JsonResponse({'error': 'Email not found'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def update_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        if new_password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})
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
            data = json.loads(request.body)
            usertype = data.get('usertype')
            email = data.get('email')
            if usertype == 'instructor':
                user_data = Instructor.find_instructor_by_email(email)
            elif usertype == 'candidate':
                user_data = Candidate.find_candidate_by_email(email)
            else:
                return JsonResponse({'error': 'Invalid user type'}, status=400)
            if user_data:
                return JsonResponse({'message': 'User found successfully', 'user_data': user_data})
            else:
                return JsonResponse({'error': 'User not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def change_account_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        new_status = data.get('status')
        user_type = data.get('userType')
        if not email or not new_status or not user_type:
            return JsonResponse({'success': False, 'message': 'Missing data.'}, status=400)
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
        return JsonResponse({'success': False, 'message': 'Invalid user type.'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

def delete_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        user_type = data.get('usertype')
        if not email or not user_type:
            return JsonResponse({'success': False, 'message': 'Missing data.'}, status=400)
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
        return JsonResponse({'success': False, 'message': 'Invalid user type.'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


from django.views.decorators.http import require_GET
from django.http import JsonResponse
import psutil
from django.db import connection


@require_GET
def get_dashboard_data(request):
    try:
        # Compute the server load
        server_load = psutil.cpu_percent(interval=1)

        # Check MongoDB status
        database_status = MongoDBConnection.check_connection()  # Call the model function

        # Prepare the data dictionary with precomputed values
        data = {
            'success': True,
            'candidates': Candidate.get_count(),
            'instructors': Instructor.get_count(),
            'ScheduledAssessments': QuestionDB.get_assessment_count("scheduled"),
            'ActiveAssessments': QuestionDB.get_assessment_count("active"),
            'endedAssessments': QuestionDB.get_assessment_count("ended"),
            'UnactiveAssessments': QuestionDB.get_assessment_count("not scheduled"),
            'system_status': {
                'server_load': f"{server_load}%",
                'database_status': database_status
            }
        }

        # Return the data as a JSON response
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# Instructor views
def instructor_login(request):
    if request.session.get('instructor_email'):
        return redirect('instructor_dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        instructor = Instructor.verify_instructor_login(email, password)
        if isinstance(instructor, str):
            messages.error(request, instructor)
        elif instructor:
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
    return render(request, 'instructor/Instructor_schedule.html', {'assessments': assessments})

def instructor_dashboard(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    QuestionDB.update_assessment_statuses()
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
    return render(request, 'instructor/Instructor_usermanagement.html', {'candidates': can})

def instructor_create_assessment(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request, 'instructor/Instructor_create_assessment.html')

def instructor_review_submission(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request, 'instructor/Instructor_review_submission.html')

def instructor_report(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request, 'instructor/Instructor_report.html')

def instructor_settings(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
        return redirect('instructor_login')
    return render(request, 'instructor/Instructor_settings.html')

def instructor_invitation(request):
    if 'instructor_email' not in request.session:
        messages.error(request, 'Please log in again to continue.')
    assessments = QuestionDB.get_all_schedule_assessment()
    candidates = Candidate.get_all_candidates()
    return render(request, 'instructor/Instructor_invitation.html', {'assessments': assessments, 'candidates': candidates})

def invitation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_emails = data.get('email')
            assessment_name = data.get('assessment_name')
            success = QuestionDB.update_assessment_emails(assessment_name, selected_emails)
            if success:
                return JsonResponse({'success': True, 'message': 'Invitations sent and emails added successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Assessment not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An error occurred while processing your request.'}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

# Candidate Views

def candidate_registration(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Candidate.find_candidate_by_email(email):
                messages.error(request, 'Email already registered.')
                return redirect('candidate_login')
            profile_image = request.FILES.get('profile_image')
            image_id = Candidate.store_image(profile_image)
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
                "profile_image_id": image_id
            }
            Candidate.add_candidate(candidate_data)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('candidate_login')
    else:
        form = SignupForm()
    return render(request, 'candidate/Candidate_registration.html', {'form': form})

def candidate_login(request):
    if request.session.get('candidate_email'):
        return redirect('candidate_dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        candidate = Candidate.verify_candidate_login(email, password)
        if isinstance(candidate, str):
            messages.error(request, candidate)
        elif candidate:
            request.session['candidate_email'] = candidate['email']
            return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    return render(request, 'candidate/Candidate_login.html')

def candidate_dashboard(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')
    QuestionDB.update_assessment_statuses()
    candidate_email = request.session['candidate_email']
    assessments = QuestionDB.get_invited_assessments(candidate_email)
    return render(request, 'candidate/Candidate_dashboard.html', {'assessments': assessments})
from urllib.parse import unquote
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

def get_decoded_assessment_name(request, assessment_name):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return None, redirect('candidate_login')
    return unquote(assessment_name), None

def candidate_preassessment(request, assessment_name):
    assessment_name, redirect_response = get_decoded_assessment_name(request, assessment_name)
    if redirect_response:
        return redirect_response
    return render(request, 'candidate/Candidate_preassesment.html', {"assessment_name": assessment_name})

def system_check(request, assessment_name):
    assessment_name, redirect_response = get_decoded_assessment_name(request, assessment_name)
    if redirect_response:
        return redirect_response

    if request.method == 'POST':
        # System checks simulation
        internet_check = request.is_ajax() and request.META.get('HTTP_REFERER') is not None
        camera_check = True
        microphone_check = True

        feedback = {
            'internet': 'Internet connection is available.' if internet_check else 'No internet connection detected.',
            'camera': 'Camera access is granted.',
            'microphone': 'Microphone access is granted.',
        }

        all_checks_passed = internet_check and camera_check and microphone_check
        return JsonResponse({
            'success': all_checks_passed,
            'feedback': feedback,
        })

    return render(request, 'candidate/System_check.html', {"assessment_name": assessment_name})

def candidate_access(request, assessment_name):
    assessment_name, redirect_response = get_decoded_assessment_name(request, assessment_name)
    if redirect_response:
        return redirect_response
    print(assessment_name)  # Debugging
    return render(request, 'candidate/System_check.html', {"assessment_name": assessment_name})

def candidate_assessment(request, assessment_name):
    assessment_name, redirect_response = get_decoded_assessment_name(request, assessment_name)
    if redirect_response:
        return redirect_response
    candidate_email = request.session['candidate_email']
    assessment =QuestionDB.fetch_Assessment(assessment_name,candidate_email)
    mcqs = assessment.get("mcq", [])
    assessment_id= assessment["assessment_id"]
    return render(request, 'candidate/Candidate_assessment.html', {"mcqs": mcqs,"assessment":assessment,"assessment_name": assessment_id})

def candidate_assessment_choice(request, assessment_name):
    assessment_name, redirect_response = get_decoded_assessment_name(request, assessment_name)
    if redirect_response:
        return redirect_response
    return render(request, 'candidate/Candidate_assessment_choice.html', {"assessment_name": assessment_name})

def candidate_coding_test(request, assessment_name):
    assessment_name, redirect_response = get_decoded_assessment_name(request, assessment_name)
    if redirect_response:
        return redirect_response
    candidate_email = request.session['candidate_email']
    assessment =QuestionDB.fetch_Assessment(assessment_name,candidate_email)
    coding_questions = assessment.get("coding", [])
    assessment_id= assessment["assessment_id"]
    return render(request, 'candidate/Candidate_coding_test.html', {"assessment_name": assessment_id,"coding_questions":coding_questions,"assessment":assessment})

def submit_coding_test(request):
    if request.method == 'POST':
        # Retrieve the submitted answers
        submitted_answers = {}
        print(request.POST)
        for key in request.POST:
            # Ensure we're only capturing answers and not other form fields (like CSRF token)
            if key.startswith('answer_'):
                submitted_answers[key] = request.POST[key]

        # Process the submitted answers as needed
        # For example, you can save them to the database, evaluate them, etc.

        # Debug: Print the submitted answers (or handle them as needed)
        print(submitted_answers)
           # Add a success message
        messages.success(request, "Assessment submitted successfully.")

        # Redirect to the dashboard or any desired page
        return redirect('candidate_dashboard')

    # If the request method is not POST, you may want to render the form again or show an error
    return HttpResponse("Invalid request method.")


def candidate_profile(request):
    if 'candidate_email' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('candidate_login')
    candidate_email = request.session['candidate_email']
    candidate = Candidate.find_candidate_by_email(candidate_email)
    image = Candidate.get_image(candidate.get('profile_image_id'))
    candidate['profile_image'] = image
    return render(request, 'candidate/Candidate_profile.html', {"profile": candidate})

def candidate_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('candidate_login')

#Admin Views
def schedule_assessment(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    if request.method == 'POST':
        assessment_name = request.POST.get('assessment_name')
        assessment_date = request.POST.get('assessment_date')
        assessment_time = request.POST.get('assessment_time')
        duration = request.POST.get('assessment_duration')
        QuestionDB.schedule_assessment_in_db(assessment_name, assessment_date,assessment_time,duration)
        assessments = QuestionDB.get_all_assessment()
        messages.success(request, 'Assessment scheduled successfully!')
        return render(request, 'admin/Admin_assessment.html', {'assessments': assessments})
    return render(request, 'admin/Admin_assessment.html')

def admindashboard(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    QuestionDB.update_assessment_statuses()
    return render(request, 'admin/Admin_dashboard.html')

def Admin_invite(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    assessments = QuestionDB.get_all_schedule_assessment()
    candidates = Candidate.get_all_candidates()
    return render(request, 'admin/Admin_invite.html', {'assessments': assessments, 'candidates': candidates})

def aiproctor(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    return render(request, 'admin/Admin_aiproctor.html')

def assessment(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    assessments = QuestionDB.get_all_assessment()
    return render(request, 'admin/Admin_assessment.html', {'assessments': assessments})
QuestionDB.generate_assessment_id()
def manualquestionupload(request):
    if 'admin_id' not in request.session or request.session.get('instructor_email'):
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    question_db = QuestionDB()
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            assessment_name = data.get('assessment_name', '')
            status = data.get('status', 'not scheduled')
            schedule = data.get('schedule', {})
            created_at = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            updated_at = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            mcq_questions = data.get('mcq', [])
            coding_questions = data.get('coding', [])
            candidates = data.get('candidates', [])
            tags = data.get('tags', [])
            if not assessment_name:
                return JsonResponse({'error': 'Assessment name is required.'}, status=400)

            assessment_id=QuestionDB.generate_assessment_id()

            assessment_document = {
                'assessment_name': assessment_name,
                'assessment_id':assessment_id,
                'status': status,
                'schedule': {
                    'date': schedule.get('date', ''),
                    'time': schedule.get('time', ''),
                    'duration': schedule.get('duration', '')
                },
                'created_at': created_at,
                'updated_at': updated_at,
                'mcq': mcq_questions,
                'coding': coding_questions,
                'candidates': candidates,
                'tags': tags
            }
            question_db.insert_assessment(assessment_document)
            return JsonResponse({'message': 'Assessment submitted successfully!'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    return render(request, 'admin/Admin_manualquestionupload.html')

def delete_assessment(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        assessment_id = data.get('assessment_id')
        if not assessment_id:
            return JsonResponse({'success': False, 'message': 'Assessment ID is required.'})
        try:
            deleted = QuestionDB.delete_assessment(assessment_id)
            if deleted:
                return JsonResponse({'success': True, 'message': 'Assessment deleted successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Assessment not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def report(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    return render(request, 'admin/Admin_report.html')

def admin_settings(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    return render(request, 'admin/Admin_settings.html')

def usermanagement(request):
    if 'admin_id' not in request.session:
        messages.warning(request, 'Please log in to continue.')
        return redirect('admin_login')
    candidates = Candidate.get_all_candidates()
    instructors = Instructor.get_all_instructors()
    return render(request, 'admin/Admin_usermanagement.html', {'candidates': candidates, 'instructors': instructors})

def admin_login(request):
    if request.method == 'POST':
        admin_id = request.POST.get('adminid')
        password = request.POST.get('password')
        admin_credentials = Admin.get_admin_credentials(admin_id)
        if admin_credentials and admin_credentials['password'] == password:
            request.session['admin_id'] = admin_id
            return redirect('admindashboard')
        else:
            messages.error(request, 'Invalid Admin ID or Password')
            return render(request, 'admin/Admin_login.html')
    else:
        return render(request, 'admin/Admin_login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')



detector = dlib.get_frontal_face_detector()

def stream_camera(request):
    if request.method == 'GET':
        return render(request, 'candidate/candidate_assesment.html')

def proctoring_view(request):
    if request.method == 'POST':
        frame_file = request.FILES.get('frame')
        if frame_file:
            nparr = np.frombuffer(frame_file.read(), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 0)
            num_faces_detected = len(rects)
            if num_faces_detected > 1:
                screenshot_path = os.path.join('static', 'image', f'screenshot_{int(time.time())}.jpg')
                cv2.imwrite(screenshot_path, frame)
                return JsonResponse({"error": "More than one face detected.", "screenshot": screenshot_path})
            return JsonResponse({"message": "Frame received", "num_faces": num_faces_detected})
    return JsonResponse({"message": "Invalid request."})
def create_candidate_pdf(email):
    print("Creating PDF document...")

    data = Candidate.find_candidate_by_email(email)
    if not data:
        print(f"No candidate found for email: {email}")
        return

    template_path = os.path.join(getattr(settings, 'STATICFILES_DIRS', [''])[0], 'file', 'CandidateDetailTemplate.pdf')
    if not os.path.exists(template_path):
        print("Template path does not exist:", template_path)
        return

    temp_pdf_path = email + "_temp.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)

    line_y_position = letter[1] - 200
    margin_below_line = 5.25 * 28.35

    profile_image_path = Candidate.get_image(data.get('profile_image_id'))
    if profile_image_path:
        image_x_position = letter[0] - 18 * 28.35  # Move it to the left (3 cm from the right edge)
        image_y_position = line_y_position + 10
        image_width = 2.5 * 28.35
        image_height = 2.5 * 28.35
        c.drawImage(profile_image_path, image_x_position, image_y_position, width=image_width, height=image_height)
    else:
        print("Profile image not found for ID:", data.get('profile_image_id'))

    print("Preparing candidate details...")
    details = [
        ['Field', 'Value'],
        ['First Name', data.get('first_name', '')],
        ['Last Name', data.get('last_name', '')],
        ['Dob', data.get('dob', '')],
        ['Gender', data.get('gender', '')],
        ['Mobile', data.get('mobile', '')],
        ['Email', data.get('email', '')],
        ['Address', data.get('address', '')],
        ['State', data.get('state', '')],
        ['Country', data.get('country', '')],
        ['Pincode', data.get('pincode', '')],
        ['Qualification', data.get('qualification', '')],
        ['Institution', data.get('institution', '')],
        ['Status', data.get('status', '')],
        ['Profile Image Id', str(data.get('profile_image_id', ''))],
    ]

    print("Creating table...")
    table = Table(details)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#2173D8")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    print("Table created.")

    table_x_position = 3 * 28.35
    table_y_position = line_y_position - margin_below_line - 200
    table.wrapOn(c, letter[0], letter[1])
    table.drawOn(c, table_x_position, table_y_position)

    c.save()

    print("Merging with the letterhead template...")
    existing_pdf = PdfReader(template_path)
    temp_pdf = PdfReader(temp_pdf_path)
    output = PdfWriter()

    existing_page = existing_pdf.pages[0]
    temp_page = temp_pdf.pages[0]
    existing_page.merge_page(temp_page)

    output.add_page(existing_page)

    final_pdf_path = email + ".pdf"
    with open(final_pdf_path, "wb") as output_stream:
        output.write(output_stream)

    os.remove(temp_pdf_path)

    print("PDF saved successfully:", final_pdf_path)


create_candidate_pdf("balachandarsanthoshkumar111@gmail.com")