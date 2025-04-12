from django import forms
from .models import SessionCoaching

class SessionCoachingForm(forms.ModelForm):
    class Meta:
        model = SessionCoaching
        fields = ['mentor', 'topic', 'start_time', 'end_time', 'description', 'students']


