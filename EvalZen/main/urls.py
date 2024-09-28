from django.urls import path
from .views import  (candidate_access, candidate_coding_test, chatbot_view, features, forgotpassword, index,instructor_logout,instructor_create_assessment, instructor_dashboard,candidate_logout,instructor_login,instructor_registration, candidate_login,candidate_registration,candidate_dashboard,candidate_preassesment,candidate_assesment,contact_us,admindashboard,aiproctor,assessment, instructor_report, instructor_review_submission, instructor_schedule, instructor_settings, instructor_usermanagement,manualquestionupload,report,settings, submit_feedback, system_check,usermanagement,admin_login,canididate_assessment_choice)

urlpatterns = [
    path('', index, name='index'),  # This should match the root URL
    path('feedback/', submit_feedback, name='feedback'),
    path('features/', features, name='features'),
    path('forgotpassword/', forgotpassword, name='forgotpassword'),
    #instructor
    path('instructor_login/', instructor_login, name='instructor_login'),
    path('instructor_registration/', instructor_registration, name='instructor_registration'),
    path('instructor_dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('instructor_schedule/', instructor_schedule, name='instructor_schedule'),
    path('instructor_usermanagement/', instructor_usermanagement, name='instructor_usermanagement'),
    path('instructor_create_assessment/', instructor_create_assessment, name='instructor_create_assessment'),
    path('instructor_review_submission/', instructor_review_submission, name='instructor_review_submission'),
    path('instructor_report/', instructor_report, name='instructor_report'),
    path('instructor_settings/', instructor_settings, name='instructor_settings'),
    path('instructor_logout/',instructor_logout, name='instructor_logout'),


    
    #candidate
    path('candidate_logout/', candidate_logout, name='candidate_logout'),
    path('candidate_login/', candidate_login, name='candidate_login'),
    path('candidate_registration/', candidate_registration, name='candidate_registration'),
    path('candidate_dashboard/', candidate_dashboard, name='candidate_dashboard'),
    path('candidate_access/', system_check, name='candidate_access'),
    path('candidate_preassesment/', candidate_preassesment, name='candidate_preassesment'),
    path('candidate_assesment/', candidate_assesment, name='candidate_assesment'),
    path('Assessment_choice/', canididate_assessment_choice, name='candidate_assesment_choice'),
    path('candidate_coding_test/', candidate_coding_test, name='candidate_coding_test'),
    path('contact_us/', contact_us, name='contact_us'),
    #admin
    path('Admin_dashboard/',admindashboard,name='admindashboard'),
    path('Admin_aiproctor/',aiproctor,name='aiproctor'),
    path('Admin_assessment/',assessment,name='adminassessment'),
    path('Admin_manualquestionupload/',manualquestionupload,name='manualquestionupload'),
    path('Admin_report/',report,name='report'),
    path('Admin_settings/',settings,name='settings'),
    path('Admin_usermanagement/',usermanagement,name='usermanagement'),
    path('Admin_login/',admin_login,name='adminlogin'),
    path('chatbot/', chatbot_view, name='chatbot_view'),




    
]
