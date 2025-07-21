"""
URL configuration for mentorship project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from mentorship_app.views import (
    MentorshipRequestViewSet,
    SessionViewSet,
    home, dashboard, mentorship_request_view,
    about, features, contact, signup, apply_to_session,
    apply_to_mentorship,
    
)
from mentorship_app.models import SessionCoaching
from mentorship_app.views import create_session_view
from mentorship_app.views import SessionCoachingAPI
from mentorship_app.views import CustomLoginView
from mentorship_app.views import dashboard_student
from mentorship_app.views import signup_student
from django.contrib.auth.views import LogoutView
from mentorship_app.views import custom_logout
from mentorship_app.views import CustomLoginView

from mentorship_app.views import videos_list, quiz_list, demande_session
from mentorship_app.views import apply_to_session
from mentorship_app import views
from mentorship_app.views import add_video 
from mentorship_app.views import add_quiz
from django.contrib.auth import views as auth_views
from mentorship_app.views import advanced_quiz_view
from mentorship_app.views import submit_quiz_answers

router = DefaultRouter()
router.register(r'mentorship_requests', MentorshipRequestViewSet)
router.register(r'sessions', SessionViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('dashboard/', dashboard, name='dashboard'),  
    path('mentorship_requests/', mentorship_request_view, name='mentorship_request'),
    path('about/', about, name='about'),  
    path('features/', features, name='features'),  
    path('contact/', contact, name='contact'),  
    path('signup/', signup, name='signup'), 
    

    path('login/', CustomLoginView.as_view(), name='login'),

    path('api/', include(router.urls)),  
    path('create_session/', create_session_view, name='create_session'),
    path('api/sessions/', SessionCoachingAPI.as_view(), name='api_sessions'),
    
   
    path('logout/', custom_logout, name='logout'),
    path('videos/', videos_list, name='videos_list'),
    path('dashboard_student/', dashboard_student, name='dashboard_student'),
    path('signup/student/', signup_student, name='signup_student'),
    path('quizzes/', quiz_list, name='quiz_list'),
    path('sessions/apply/<int:session_id>/', apply_to_session, name='apply_to_session'),
    path('apply_to_mentorship/', views.apply_to_mentorship, name='apply_to_mentorship'),
    path('videos/add/', add_video, name='add_video'),
    path('quizzes/add/', add_quiz, name='add_quiz'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('quizzes/advanced/', advanced_quiz_view, name='quiz_lists'),

    path('quizzes/submit/', submit_quiz_answers, name='submit_quiz_answers'),

    path('demande_session/', views.demande_session, name='demande_session'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('quiz/add/', views.quiz_add, name='quiz_add'),
    path('quiz/edit/<int:quiz_id>/', views.quiz_edit, name='quiz_edit'),
    path('quiz/delete/<int:quiz_id>/', views.quiz_delete, name='quiz_delete'),
    path('sessions/cancel/<int:session_id>/', views.cancel_application, name='cancel_application'),
    path('custom-requests/delete/<int:request_id>/', views.delete_custom_request, name='delete_custom_request'),
    path('videos/add/', views.video_add, name='video_add'),
    path('videos/edit/<int:video_id>/', views.video_edit, name='video_edit'),
    path('videos/delete/<int:video_id>/', views.video_delete, name='video_delete'),
 
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

