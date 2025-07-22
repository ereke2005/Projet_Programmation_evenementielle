from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from .models import MentorshipRequest, Session
from .serializers import MentorshipRequestSerializer, SessionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Mentor, Eleve, SessionCoaching
from .serializers import SessionCoachingSerializer
from django.http import JsonResponse
from .models import SessionCoaching, Mentor, Eleve, MentorshipRequest
from .forms import SessionCoachingForm
from django.core.mail import send_mail
from django.db import models
from mentorship_app.models import Eleve
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import os
from django.contrib.auth.models import User
from mentorship_app.models import Mentor
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model, logout
User = get_user_model()
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import logging
logger = logging.getLogger(__name__)
from django.contrib.auth.forms import AuthenticationForm


from django.contrib.auth.hashers import make_password
from mentorship_app.models import Video, Quiz,  QuizAnswer
from mentorship_app.models import MentorshipApplication
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Video, Domain
from django.contrib import messages
from .forms import PersonalizedSessionRequestForm
from .models import Quiz, Video
from .models import PersonalizedSessionRequest
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponseForbidden

from django.shortcuts import render



def is_mentor(user):
    return user.is_authenticated and user.is_mentor


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

from .models import ContactMessage

@login_required
def dashboard(request):
   
    sessions = SessionCoaching.objects.filter(mentor__user=request.user).order_by('start_time')

    
    personalized_requests = PersonalizedSessionRequest.objects.all().order_by('-submitted_at')

   
    messages_recus = ContactMessage.objects.order_by('-created_at')[:5]
    total_messages = ContactMessage.objects.count()

    return render(request, 'dashboard.html', {
        'sessions': sessions,
        'personalized_requests': personalized_requests,
        'messages_recus': messages_recus,
        'total_messages': total_messages,
    })

    
@login_required
def mentorship_request_view(request):
    return render(request, 'mentorship_request.html')

def about(request):
    return render(request, 'about.html')

def features(request):
    return render(request, 'features.html')

def signup_student(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        level = request.POST.get('level') 

        
        if User.objects.filter(username=username).exists():
            return render(request, 'signup_student.html', {
                'error': "Nom d'utilisateur déjà pris."
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'signup_student.html', {
                'error': "Email déjà utilisé."
            })

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_student=True,
            is_active=False  
        )

        user.save()
        Eleve.objects.create(user=user, level=level)

        send_activation_email(request, user)
        return render(request, 'signup_success.html', {'username': username})

    return render(request, 'signup_student.html')

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
       
        user.is_active = False
        user.save()

        print(f"Utilisateur créé : {user}, Type : {type(user)}")

        if isinstance(user, User):
            mentor = Mentor.objects.create(user=user)
            send_activation_email(request, user)
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




def send_activation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    activation_link = request.build_absolute_uri(
        reverse('activate', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Activation de votre compte Mentorship'
    message = f"Bonjour {user.username},\n\nVeuillez cliquer sur le lien suivant pour activer votre compte :\n{activation_link}\n\nMerci."

    send_mail(subject, message, 'noreply@mentorship.com', [user.email], fail_silently=False)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activation_success.html', {'username': user.username})
    else:
        return render(request, 'activation_failed.html')

@login_required
def create_session_view(request):
    if request.method == "POST":
        form = SessionCoachingForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.mentor = request.user.mentor_profile 
            session.save()
            form.save_m2m() 
            return redirect('dashboard')  
    else:
        form = SessionCoachingForm()

    return render(request, "create_sessions.html", {"form": form})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm
    
    def get_success_url(self):
        user = self.request.user
        if user.is_student:
            return reverse_lazy('dashboard_student')  
        elif user.is_mentor:
            return reverse_lazy('dashboard') 
        return reverse_lazy('dashboard') 


@login_required
def videos_list(request):
    videos = Video.objects.all()
    return render(request, 'videos_list.html', {'videos': videos})
@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})

@login_required
def custom_logout(request):
    logout(request)
    return redirect('home') 

@login_required
def mentorship_request_view(request):
    if request.method == "POST":
        interest = request.POST.get("interest")
        language = request.POST.get("language")
        time_zone = request.POST.get("time_zone")
        notes = request.POST.get("notes")

        
        MentorshipRequest.objects.create(
            interest=interest,
            language=language,
            time_zone=time_zone,
            notes=notes
        )

        return render(request, "mentorship_request_success.html", {"interest": interest})

    return render(request, "mentorship_request.html")

@require_POST
@login_required
def apply_to_session(request, session_id):
    session = get_object_or_404(SessionCoaching, pk=session_id)
    student = request.user.student_profile
    session.students.add(student)
    return redirect('dashboard_student')

@login_required
def dashboard_student(request):
    student = request.user.student_profile
    sessions_inscrites = SessionCoaching.objects.filter(students=student)
    sessions_publiques = SessionCoaching.objects.filter(is_public=True)
    mentorships = MentorshipRequest.objects.all()

    sessions_postulees_ids = sessions_inscrites.values_list('id', flat=True)
    mentorships_applied_ids = MentorshipApplication.objects.filter(student=student).values_list('mentorship_request_id', flat=True)

    demandes_personnalisees = PersonalizedSessionRequest.objects.filter(user=request.user)

    return render(request, 'dashboard_student.html', {
        'user': request.user,
        'sessions_inscrites': sessions_inscrites,
        'sessions_publiques': sessions_publiques,
        'mentorships': mentorships,
        'sessions_postulees_ids': sessions_postulees_ids,
        'mentorships_applied_ids': mentorships_applied_ids,
        'demandes_personnalisees': demandes_personnalisees,
    })



def public_sessions_list(request):
    sessions = SessionCoaching.objects.filter(is_public=True)
    return render(request, 'public_sessions.html', {'sessions': sessions})




def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        
        if not name or not email or not message:
            messages.error(request, "Tous les champs sont obligatoires.")
            return redirect('contact')

        
        subject = f"Message de contact de {name}"
        full_message = f"Nom: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                email,  
                ['rachelbinawai@gmail.com'],  
                fail_silently=False,
            )

            messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons rapidement.")
            return redirect('contact')

        except Exception as e:
            messages.error(request, "Erreur lors de l'envoi de votre message. Essayez plus tard.")
            return redirect('contact')

    return render(request, "contact.html")


@login_required
@require_POST
def apply_to_mentorship(request):
    student = request.user.student_profile
    selected_ids = request.POST.getlist('mentorship_requests')

    for req_id in selected_ids:
        mentorship_request = MentorshipRequest.objects.get(id=req_id)
      
        MentorshipApplication.objects.get_or_create(
            student=student,
            mentorship_request=mentorship_request
        )

    return redirect('dashboard_student')


@login_required
def add_video(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')

        Video.objects.create(
            title=title,
            description=description,
            video_file=video_file,  
            uploaded_by=request.user 
        )

        messages.success(request, "Vidéo ajoutée avec succès.")
        return redirect('dashboard')

    return render(request, 'add_video.html')




@login_required
def add_quiz(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        correct_answer = request.POST.get('correct_answer')

        Quiz.objects.create(
            question=question,
            option1=option1,
            option2=option2,
            option3=option3,
            correct_answer=correct_answer
        )

        messages.success(request, "Quiz créé avec succès.")
        return redirect('dashboard')

    return render(request, 'add_quiz.html')



@login_required
def submit_quiz_answers(request):
    if request.method == "POST":
        student = request.user.student_profile

        for key, value in request.POST.items():
            if key.startswith("response_"):
                quiz_id = key.split("_")[1]
                quiz = Quiz.objects.get(id=quiz_id)

                
                QuizAnswer.objects.create(
                    quiz=quiz,
                    student=student,
                    selected_option=value
                )

        messages.success(request, "Réponses envoyées avec succès !")
        return redirect("quiz_list")

    return HttpResponseForbidden("Méthode non autorisée.")

@login_required
def advanced_quiz_view(request):
    student = request.user.student_profile
    quizzes = Quiz.objects.all()
    domain_filter = request.GET.get('domain')
    if domain_filter:
        quizzes = quizzes.filter(domain__icontains=domain_filter)
    context = {
        'quizzes': quizzes,
    }
    return render(request, 'quiz_lists.html', context)


@login_required
def submit_quiz_answers(request):
    if request.method == "POST":
        student = request.user.student_profile

        for key, value in request.POST.items():
            if key.startswith("response_"):
                quiz_id = key.split("_")[1]
                quiz = Quiz.objects.get(id=quiz_id)

                QuizAnswer.objects.create(
                    quiz=quiz,
                    student=student,
                    selected_option=value
                )

        messages.success(request, "Réponses envoyées avec succès !")
        return redirect("quiz_lists")

    return HttpResponseForbidden("Méthode non autorisée.")




@login_required
def submit_quiz_answers(request):
    if request.method == "POST":
        student = request.user.student_profile
        correct_count = 0
        total = 0

        for key, value in request.POST.items():
            if key.startswith("response_"):
                quiz_id = key.split("_")[1]
                quiz = Quiz.objects.get(id=quiz_id)
                total += 1

                QuizAnswer.objects.create(
                    quiz=quiz,
                    student=student,
                    selected_option=value
                )

                if value == quiz.correct_answer:
                    correct_count += 1

      
        if correct_count == total:
            messages.success(request, f"🎉 Bravo ! Vous avez obtenu un score parfait : {correct_count}/{total}.")
        else:
            messages.info(request, f"Vous avez répondu correctement à {correct_count} questions sur {total}.")

        return redirect("quiz_lists")

    return HttpResponseForbidden("Méthode non autorisée.")

@login_required
def demande_session(request):
    if request.method == 'POST':
        form = PersonalizedSessionRequestForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.user = request.user
            demande.save()
            messages.success(request, "Votre demande a bien été envoyée !")
            return redirect('demande_session')  
    else:
        form = PersonalizedSessionRequestForm()
    return render(request, 'demande_session.html', {'form': form})

def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        quiz.question = request.POST.get('question')
        quiz.option1 = request.POST.get('option1')
        quiz.option2 = request.POST.get('option2')
        quiz.option3 = request.POST.get('option3')
        quiz.correct_answer = request.POST.get('correct_answer')
        quiz.difficulty = request.POST.get('difficulty')
        quiz.save()
        return redirect('quiz_list')

    return render(request, 'quiz_form.html', {
        'quiz': quiz,
        'action': 'Modifier',
        'DIFFICULTY_CHOICES': [
            ('basic', 'Basique'),
            ('intermediate', 'Intermédiaire'),
            ('advanced', 'Avancé'),
        ]
    })

def quiz_add(request):
    if request.method == 'POST':
        Quiz.objects.create(
            question=request.POST.get('question'),
            option1=request.POST.get('option1'),
            option2=request.POST.get('option2'),
            option3=request.POST.get('option3'),
            correct_answer=request.POST.get('correct_answer'),
            difficulty=request.POST.get('difficulty')
        )
        return redirect('quiz_list')

    return render(request, 'quiz_form.html', {
        'action': 'Ajouter',
        'quiz': {},
        'DIFFICULTY_CHOICES': [
            ('basic', 'Basique'),
            ('intermediate', 'Intermédiaire'),
            ('advanced', 'Avancé'),
        ]
    })

def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    return redirect('quiz_list')

@login_required
def cancel_application(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(SessionCoaching, id=session_id, is_public=True)
        student = request.user.student_profile
        session.students.remove(student)
        messages.success(request, "Votre participation à la session a été annulée.")
    return redirect('dashboard_student')

@login_required
def delete_custom_request(request, request_id):
    if request.method == 'POST':
        demande = get_object_or_404(PersonalizedSessionRequest, id=request_id, user=request.user)
        demande.delete()
        messages.success(request, "Votre demande personnalisée a été supprimée.")
    return redirect('dashboard_student')

@login_required
def video_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')

        if title and video_file:
            Video.objects.create(
                title=title,
                description=description,
                video_file=video_file,
                uploaded_by=request.user
            )
            return redirect('videos_list')

    return render(request, 'video_form.html', {'action': 'Ajouter'})

@login_required
def video_edit(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    if request.method == 'POST':
        video.title = request.POST.get('title')
        video.description = request.POST.get('description')

       
        if request.FILES.get('video_file'):
            video.video_file = request.FILES.get('video_file')

        video.save()
        return redirect('videos_list')

    return render(request, 'video_form.html', {'video': video, 'action': 'Modifier'})


@login_required
def video_delete(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        video.delete()
        return redirect('videos_list')
    return render(request, 'video_confirm_delete.html', {'video': video})

def upload_pdf(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('pdf_file')
        if uploaded_file:
           
            save_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
           
            with open(save_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
           
            return redirect('dashboard')
    return render(request, 'upload.html')


@login_required
def videos_lists(request):
    videos = Video.objects.all()
    return render(request, 'video_lists.html', {'videos': videos})
