from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import MentorshipRequest, Session
from .serializers import MentorshipRequestSerializer, SessionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Mentor, Eleve, SessionCoaching
from .serializers import SessionCoachingSerializer

from django.http import JsonResponse
from .models import SessionCoaching, Mentor, Eleve
from .forms import SessionCoachingForm
from django.core.mail import send_mail

import os
from django.contrib.auth.models import User
from mentorship_app.models import Mentor
from django.core.files.storage import default_storage

from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import logging
logger = logging.getLogger(__name__)
from django.contrib.auth.forms import AuthenticationForm


class MentorshipRequestViewSet(viewsets.ModelViewSet):
    queryset = MentorshipRequest.objects.all()
    serializer_class = MentorshipRequestSerializer

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class SessionCoachingAPI(APIView):
    def get(self, request):
        sessions = SessionCoaching.objects.all()
        serializer = SessionCoachingSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SessionCoachingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Session créée avec succès !"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Erreur lors de la création de la session", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def mentorship_request_view(request):
    return render(request, 'mentorship_request.html')

def about(request):
    return render(request, 'about.html')

def features(request):
    return render(request, 'features.html')

@login_required
def dashboard(request):
    
    sessions = SessionCoaching.objects.filter(students__user=request.user)
    return render(request, 'dashboard.html', {'sessions': sessions})

def contact(request):
    if request.method == "POST":
        # Récupérer les données du formulaire
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Option : Envoyer un email (si configuré)
        send_mail(
            subject=f"Nouveau message de {name}",
            message=message,
            from_email=email,
            recipient_list=['support@mentorship.com'],  # Adresse destinataire
        )

        # Afficher un message de confirmation (ou rediriger)
        return HttpResponse("Merci pour votre message, nous vous répondrons rapidement.")

    return render(request, "contact.html")
    


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cv_file = request.FILES.get('cv')
        certificate_file = request.FILES.get('certificate')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': "Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre."})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': "Cet e-mail est déjà utilisé. Veuillez en choisir un autre."})

        user = User.objects.create_user(username=username, email=email, password=password)

        print(f"Utilisateur créé : {user}, Type : {type(user)}")

        if isinstance(user, User):
            mentor = Mentor.objects.create(user=user)
            save_directory = os.path.join('uploads', 'mentors', username)
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            if cv_file:
                cv_path = default_storage.save(os.path.join(save_directory, 'cv_' + cv_file.name), cv_file)

            if certificate_file:
                certificate_path = default_storage.save(os.path.join(save_directory, 'certificate_' + certificate_file.name), certificate_file)

            return render(request, 'signup_success.html', {'username': username})
        else:
            print("Erreur : user n'est pas une instance de User")
            return render(request, 'signup.html', {'error': "Une erreur est survenue lors de la création du mentor."})

    return render(request, 'signup.html')




def create_session(request):
    if request.method == "POST":
        form = SessionCoachingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/dashboard/')  # Redirection après la création de la session
    else:
        form = SessionCoachingForm()

    return render(request, 'create_session.html', {'form': form})



def create_session_view(request):
    if request.method == "POST":
        form = SessionCoachingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirige après la création
    else:
        form = SessionCoachingForm()

    return render(request, "create_sessions.html", {"form": form})



class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm  # Utilise le formulaire intégré

    def form_invalid(self, form):
        logger.warning(f"Erreur dans le formulaire : {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard')


@login_required
def dashboard_student(request):
    return render(request, 'dashboard_student.html', {'user': request.user})




