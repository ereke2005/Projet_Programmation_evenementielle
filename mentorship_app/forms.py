from django import forms
from .models import SessionCoaching
from .models import Eleve
from .models import PersonalizedSessionRequest


class SessionCoachingForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Eleve.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Élèves à inscrire"
    )

    class Meta:
        model = SessionCoaching
        fields = ['topic', 'start_time', 'end_time', 'description', 'students', 'is_public']  
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'Date et heure de début'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'Date et heure de fin'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Décris ta session ici',
                'rows': 3
            }),
        }


class PersonalizedSessionRequestForm(forms.ModelForm):
    class Meta:
        model = PersonalizedSessionRequest
        fields = ['subject', 'details']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Sujet de votre demande'}),
            'details': forms.Textarea(attrs={'placeholder': 'Décrivez votre besoin'}),
        }

