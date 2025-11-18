from rest_framework import serializers
from .models import Registartion

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registartion
        fields = '__all__'
