
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

INVALID_CREDENTIALS_ERROR = "Credenciais de login inválidas."

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True) 
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def to_internal_value(self, data):
       
        if not data.get('username') and not data.get('email'):
            raise ValidationError({"detail": INVALID_CREDENTIALS_ERROR})

        if data.get('email') and not data.get('username'):
            try:
                user = User.objects.get(email=data['email'])
                data['username'] = user.username
            except User.DoesNotExist:
                raise ValidationError({"detail": INVALID_CREDENTIALS_ERROR})

        return super().to_internal_value(data)

    def validate(self, attrs):
        
        username = attrs.get('username')
        password = attrs.get('password')
    
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError({"detail": INVALID_CREDENTIALS_ERROR})

        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return tokens
