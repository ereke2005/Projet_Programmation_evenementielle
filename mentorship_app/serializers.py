from rest_framework import serializers
from .models import MentorshipRequest, Session
from .models import SessionCoaching, Mentor, Eleve

class MentorshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipRequest
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

from rest_framework import serializers
from .models import SessionCoaching



class SessionCoachingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionCoaching
        fields = '__all__'

