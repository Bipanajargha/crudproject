from rest_framework import serializers
from .models import Registartion
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registartion
        fields = '__all__'

class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, help_text="Confirm password")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'confirm_password')

    def validate(self, input_data):
        # Check if passwords match
        if input_data['password'] != input_data['confirm_password']:
            raise serializers.ValidationError({"message":"Password and Confirm Password do not match"})

        # Validate password strength
        try:
            validate_password(input_data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

        # Check if username or email already exists
        if User.objects.filter(username=input_data['username']).exists():
            raise serializers.ValidationError({"message": "Username already exists"})
        if User.objects.filter(email=input_data['email']).exists():
            raise serializers.ValidationError({"message": "Email has been already registered"})

        return input_data

    def create(self, validated_data):
        # Remove password1 before creating the user
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)