from django.urls import path
from .views import  (Active_Assessments,candidate_access, candidate_profile, download_assessment_report, download_proctoring_report, invitation, Unactive_Assessments, admin_logout,get_user_counts,delete_user, candidate_access, change_account_status, edit_user, instructor_invitation, proctoring_view, schedule_assessment,send_otp, update_password,verify_otp, candidate_coding_test, features, forgotpassword, index,instructor_logout,instructor_create_assessment, instructor_dashboard,candidate_logout,instructor_login,instructor_registration, candidate_login,candidate_registration,candidate_dashboard,candidate_preassesment,candidate_assesment,contact_us,admindashboard,aiproctor,assessment, instructor_report, instructor_review_submission, instructor_schedule, instructor_settings, instructor_usermanagement,manualquestionupload,report,settings, submit_feedback, system_check,usermanagement,admin_login,canididate_assessment_choice)

urlpatterns = [
    path('', index, name='index'),  # This should match the root URL
    path('feedback/', submit_feedback, name='feedback'),
    path('features/', features, name='features'),
    path('forgotpassword/', forgotpassword, name='forgotpassword'),
    path('send-otp/', send_otp, name='send-otp'),
    path('verify-otp/', verify_otp, name='verify-otp'),
    path('update-password/', update_password, name='update_password'),
        path('edit_user/', edit_user, name='edit_user'),


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
    path('instructor_invitation/', instructor_invitation, name='instructor_invitation'),
   path('invitation/',invitation,name='invitation'),

    
    #candidate
    path('candidate_logout/', candidate_logout, name='candidate_logout'),
    path('candidate_login/', candidate_login, name='candidate_login'),
        path('candidate_profile/', candidate_profile, name='candidate_profile'),
    path('candidate_registration/', candidate_registration, name='candidate_registration'),
    path('candidate_dashboard/', candidate_dashboard, name='candidate_dashboard'),
    path('candidate_access/<int:assessment_id>/', candidate_access, name='candidate_access'),

    path('candidate_access/', system_check, name='candidate_access'),
    path('candidate_preassesment/', candidate_preassesment, name='candidate_preassesment'),
    path('candidate_assesment/', candidate_assesment, name='candidate_assesment'),
    path('Assessment_choice/', canididate_assessment_choice, name='candidate_assesment_choice'),
    path('candidate_coding_test/', candidate_coding_test, name='candidate_coding_test'),
    path('contact_us/', contact_us, name='contact_us'),
    path('change_status/',change_account_status,name="change_status"),
    path('proctoring/', proctoring_view, name='proctoring'),
    #admin
    path('Admin_dashboard/',admindashboard,name='admindashboard'),
    path('Admin_aiproctor/',aiproctor,name='aiproctor'),
    path('Admin_assessment/',assessment,name='adminassessment'),
    path('Admin_manualquestionupload/',manualquestionupload,name='manualquestionupload'),
    path('Admin_report/',report,name='report'),
    path('Admin_settings/',settings,name='settings'),
    path('Admin_usermanagement/',usermanagement,name='usermanagement'),
    path('admin_login/',admin_login,name='admin_login'),
    path('Admin_logout/',admin_logout,name='adminlogout'),
    path('schedule_assessment/',schedule_assessment,name='schedule_assessment'),
    path('delete_user/', delete_user, name='delete_user'),
    path('download/assessment_report/', download_assessment_report, name='download_assessment_report'),
    path('download/proctoring_report/', download_proctoring_report, name='download_proctoring_report'),

    path('get-user-counts/', get_user_counts, name='get_user_counts'),
    path('Active-Assessments/', Active_Assessments, name='Active-Assessments'),
    path('Unactive-Assessments/', Unactive_Assessments, name='Unactive-Assessments'),  # New path

]
