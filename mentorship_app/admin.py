from django.contrib import admin
from .models import Eleve, Mentor, SessionCoaching

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'get_is_student')

    def get_username(self, obj):
        return obj.user.username  # Accès à `username` dans User
    get_username.short_description = 'Nom utilisateur'

    def get_email(self, obj):
        return obj.user.email  # Accès à `email` dans User
    get_email.short_description = 'Email'

    def get_is_student(self, obj):
        return obj.user.is_student  # Accès à `is_student` dans User
    get_is_student.short_description = 'Est élève'

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'get_is_mentor')

    def get_username(self, obj):
        return obj.user.username  # Accès à `username` dans User
    get_username.short_description = 'Nom utilisateur'

    def get_email(self, obj):
        return obj.user.email  # Accès à `email` dans User
    get_email.short_description = 'Email'

    def get_is_mentor(self, obj):
        return obj.user.is_mentor  # Accès à `is_mentor` dans User
    get_is_mentor.short_description = 'Est mentor'

@admin.register(SessionCoaching)
class SessionCoachingAdmin(admin.ModelAdmin):
    list_display = ('topic', 'mentor', 'start_time', 'end_time')
    filter_horizontal = ('students',)  # Ajout de gestion pour la relation ManyToMany avec les élèves