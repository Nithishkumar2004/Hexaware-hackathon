"""
URL configuration for EvalZen project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from admin import views as a
# from main import  views as m

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('main.urls')), 
    # path('admindashboard/',a.admindashboard,name='admindashboard'),
    # path('aiproctor/',a.aiproctor,name='aiproctor'),
    # path('assessment/',a.assessment,name='assessment'),
    # path('manualquestionupload/',a.manualquestionupload,name='manualquestionupload'),
    # path('report/',a.report,name='report'),
    # path('settings/',a.settings,name='settings'),
    # path('usermanagement/',a.usermanagement,name='usermanagements'),

    # path('', m.index, name='index'),  # This should match the root URL
    # path('instructor_login/', m.instructor_login, name='instructor_login'),
    # path('candidate_login/', m.candidate_login, name='candidate_login'),
    # path('candidate_registration/', m.candidate_registration, name='candidate_registration'),
    # path('candidate_dashboard/', m.candidate_dashboard, name='candidate_dashboard'),
    # path('candidate_preassesment/', m.candidate_preassesment, name='candidate_preassesment'),
    # path('candidate_assesment/', m.candidate_assesment, name='candidate_assesment'),
    # path('contact_us/', m.contact_us, name='contact_us'),

#  Include URLs from the main app
]
