# userprofile/serializers.py
from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'location', 'birth_date', 'profile_picture', 'gender', 'is_author',  'follow_count']
        read_only_fields = ['user']
    
    def update(self, instance, validated_data):
        """
        Atualiza o perfil do usuário autenticado. Somente permite que certos campos sejam alterados.
        """
        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.is_author = validated_data.get('is_author', instance.is_author)
        
        instance.save()
        return instance
