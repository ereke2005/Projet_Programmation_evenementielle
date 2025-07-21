from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import get_user_model




class User(AbstractUser):
    is_mentor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='Groupes auxquels cet utilisateur appartient.',
        verbose_name='groupes'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Permissions spécifiques pour cet utilisateur.',
        verbose_name='permissions utilisateur'
    )

    def __str__(self):
        return self.username


class Mentor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentor_profile")
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Mentor: {self.user.username}"


class Eleve(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    level = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.level})"

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"


class MentorshipRequest(models.Model):
    interest = models.CharField(max_length=255, default="DefaultInterest")
    language = models.CharField(max_length=50, default="English")
    time_zone = models.CharField(max_length=50, default="UTC")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SessionCoaching(models.Model):
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    topic = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    students = models.ManyToManyField(Eleve, related_name="sessions")
    is_public = models.BooleanField(default=False, verbose_name="Session publique")

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("L'heure de début doit être avant l'heure de fin.")
        if not self.topic:
            raise ValidationError("Le sujet de la session est requis.")

    def __str__(self):
        return f"{self.topic} - Mentor : {self.mentor.user.username}"

    class Meta:
        verbose_name = "Session de Coaching"
        verbose_name_plural = "Sessions de Coaching"


class SessionCoachingForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Eleve.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 6}),
        required=False,
        label="Étudiants participants"
    )

    class Meta:
        model = SessionCoaching
        fields = ['topic', 'description', 'start_time', 'end_time', 'is_public', 'students']


class Session(models.Model):
    title = models.CharField(max_length=255, default="Session par défaut")
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(default="2024-01-01 12:00")
    end_time = models.DateTimeField(default="2025-01-01 12:00")

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Domain(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name



User = get_user_model()

class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/')  
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title





class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class MentorshipApplication(models.Model):
    mentorship_request = models.ForeignKey("MentorshipRequest", on_delete=models.CASCADE, related_name="applications")
    student = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="mentorship_applications")
    date_applied = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("mentorship_request", "student")

    def __str__(self):
        return f"{self.student.user.username} a postulé pour {self.mentorship_request.interest}"

DIFFICULTY_CHOICES = [
    ('basic', 'Basique'),
    ('intermediate', 'Intermédiaire'),
    ('advanced', 'Avancé'),
]

class Quiz(models.Model):
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='basic',
        verbose_name="Niveau de difficulté"
    )

    def __str__(self):
        return self.question


class QuizAnswer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=255)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.quiz}"




class PersonalizedSessionRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    details = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.user.username} : {self.subject}"
