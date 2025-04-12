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
from mentorship_app.views import (
    MentorshipRequestViewSet,
    SessionViewSet,
    home, dashboard, mentorship_request_view,
    about, features, contact, signup
    
)
from mentorship_app.models import SessionCoaching
from mentorship_app.views import create_session_view
from mentorship_app.views import SessionCoachingAPI
from mentorship_app.views import CustomLoginView



# Définition des routes API
router = DefaultRouter()
router.register(r'mentorship_requests', MentorshipRequestViewSet)
router.register(r'sessions', SessionViewSet)

# Liste des URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Accueil
    path('dashboard/', dashboard, name='dashboard'),  # Tableau de bord
    path('mentorship_requests/', mentorship_request_view, name='mentorship_request'),
    path('about/', about, name='about'),  # Page À propos
    path('features/', features, name='features'),  # Page Fonctionnalités
    path('contact/', contact, name='contact'),  # Page Contact
    path('signup/', signup, name='signup'),  # Page Inscription
    path('api/', include(router.urls)),  # API REST Framework
    path('create_session/', create_session_view, name='create_session'),
    path('api/sessions/', SessionCoachingAPI.as_view(), name='api_sessions'),
    path('login/', CustomLoginView.as_view(), name='login'),
]

    
