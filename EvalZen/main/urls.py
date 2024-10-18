from django.urls import include, path
from .views import (
    Admin_invite, delete_assessment, candidate_access, candidate_profile, invitation, 
    admin_logout, get_dashboard_data, delete_user, change_account_status, edit_user,
    instructor_invitation, proctoring_view, schedule_assessment, send_otp, update_password,
    verify_otp, candidate_coding_test, features, forgotpassword, index, instructor_logout,
    instructor_create_assessment, instructor_dashboard, candidate_logout, instructor_login,
    instructor_registration, candidate_login, candidate_registration, candidate_dashboard,
    candidate_preassessment, candidate_assessment, contact_us, admindashboard, 
    assessment, instructor_report, instructor_review_submission, instructor_schedule,
    instructor_settings, instructor_usermanagement, manualquestionupload, report, settings,
    submit_feedback, system_check, usermanagement, admin_login, candidate_assessment_choice,
    submit_coding_test
)

# Grouping URL patterns by functionality for better organization
urlpatterns = [
    # General
    path('', index, name='index'),
    path('feedback/', submit_feedback, name='feedback'),
    path('features/', features, name='features'),
    path('forgotpassword/', forgotpassword, name='forgotpassword'),
    path('send-otp/', send_otp, name='send-otp'),
    path('verify-otp/', verify_otp, name='verify-otp'),
    path('update-password/', update_password, name='update_password'),
    path('edit_user/', edit_user, name='edit_user'),

    # Instructor URLs
    path('instructor/', include([
        path('login/', instructor_login, name='instructor_login'),
        path('registration/', instructor_registration, name='instructor_registration'),
        path('dashboard/', instructor_dashboard, name='instructor_dashboard'),
        path('schedule/', instructor_schedule, name='instructor_schedule'),
        path('usermanagement/', instructor_usermanagement, name='instructor_usermanagement'),
        path('create_assessment/', instructor_create_assessment, name='instructor_create_assessment'),
        path('manualquestionupload/', manualquestionupload, name='manualquestionupload'),
        path('review_submission/', instructor_review_submission, name='instructor_review_submission'),
        path('report/', instructor_report, name='instructor_report'),
        path('settings/', instructor_settings, name='instructor_settings'),
        path('logout/', instructor_logout, name='instructor_logout'),
        path('invitation/', instructor_invitation, name='instructor_invitation'),

        path('delete_user/', delete_user, name='delete_user'),
        path('invitationtouser/', invitation, name='invitationtouser'),
        path('dashboard-data/', get_dashboard_data, name='dashboard_data'),

    ])),

    # Candidate URLs
    path('candidate/', include([
        path('logout/', candidate_logout, name='candidate_logout'),
        path('login/', candidate_login, name='candidate_login'),
        path('registration/', candidate_registration, name='candidate_registration'),
        path('profile/', candidate_profile, name='candidate_profile'),
        path('dashboard/', candidate_dashboard, name='candidate_dashboard'),
        path('access/<str:assessment_name>/', candidate_access, name='candidate_access'),
        path('access/<str:assessment_name>/', system_check, name='candidate_access'), 
        path('preassessment/<str:assessment_name>/', candidate_preassessment, name='candidate_preassessment'),
        path('assessment/<str:assessment_name>/', candidate_assessment, name='candidate_assessment'),
        path('assessment_choice/<str:assessment_name>/', candidate_assessment_choice, name='candidate_assessment_choice'),
        path('coding_test/<str:assessment_name>/', candidate_coding_test, name='candidate_coding_test'),
    path('submit_coding_test/', submit_coding_test, name='submit_coding_test'),

        path('contact/', contact_us, name='contact_us'),
        path('proctoring/', proctoring_view, name='proctoring'),
        
    ])),

    # Admin URLs
    path('admin/', include([
        path('dashboard/', admindashboard, name='admindashboard'),
        path('assessment/', assessment, name='adminassessment'),
        path('change_status/', change_account_status, name="change_status"),
        path('manualquestionupload/', manualquestionupload, name='manualquestionupload'),
        path('report/', report, name='report'),
        path('settings/', settings, name='settings'),
        path('usermanagement/', usermanagement, name='usermanagement'),
        path('login/', admin_login, name='admin_login'),
        path('logout/', admin_logout, name='admin_logout'),
        path('invite/', Admin_invite, name='Admin_invite'),
        path('invitationtouser/', invitation, name='invitationtouser'),
        path('schedule_assessment/', schedule_assessment, name='schedule_assessment'),
        path('delete_user/', delete_user, name='delete_user'),
        path('delete_assessment/', delete_assessment, name='delete_assessment'),        
        path('dashboard-data/', get_dashboard_data, name='dashboard_data'),

    ])),
]
