from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Modèle utilisateur personnalisé
class User(AbstractUser):
    is_mentor = models.BooleanField(default=False)  # Indique si l'utilisateur est un mentor
    is_student = models.BooleanField(default=False)  # Indique si l'utilisateur est un élève

    # Ajout de `related_name` pour éviter les conflits
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

# Classe Mentor (hérite de User)
class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mentor_profile")
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Mentor: {self.user.username}"


# Classe Élève (hérite de User)
class Eleve(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    level = models.CharField(max_length=50, blank=True, null=True)  # Niveau (exemple : Débutant)

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"

class MentorshipRequest(models.Model):
    interest = models.CharField(max_length=255, default="DefaultInterest")  # Domaine d'intérêt avec valeur par défaut
    language = models.CharField(max_length=50, default="English")  # Langue préférée
    time_zone = models.CharField(max_length=50, default="UTC")  # Fuseau horaire par défaut
    notes = models.TextField(blank=True, null=True)  # Notes supplémentaires
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création automatique

# Classe SessionCoaching


class SessionCoaching(models.Model):
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name="sessions"  # Relation Mentor -> Sessions
    )
    topic = models.CharField(max_length=255)  # Sujet de la session de coaching
    start_time = models.DateTimeField()  # Début de la session
    end_time = models.DateTimeField()  # Fin de la session
    description = models.TextField(blank=True, null=True)  # Description de la session
    students = models.ManyToManyField(Eleve, related_name="sessions")  # Relation avec les élèves participant à la session

    def clean(self):
        """
        Valide les données avant de sauvegarder :
        - Vérifie que l'heure de début est avant l'heure de fin.
        - Vérifie que le sujet est fourni.
        """
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("L'heure de début doit être avant l'heure de fin.")
        if not self.topic:
            raise ValidationError("Le sujet de la session est requis.")

    def __str__(self):
        return f"{self.topic} - Mentor : {self.mentor.user.username}"

    class Meta:
        verbose_name = "Session de Coaching"
        verbose_name_plural = "Sessions de Coaching"


class Session(models.Model):
    title = models.CharField(max_length=255, default="Session par défaut")
    description = models.TextField(blank=True, null=True)  # Description de la session
    start_time = models.DateTimeField(default="2024-01-01 12:00")  # Début de la session
  
    end_time = models.DateTimeField(default="2025-01-01 12:00")

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username