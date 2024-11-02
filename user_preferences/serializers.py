# user_preferences/serializers.py
from rest_framework import serializers
from .models import NotificationSettings

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = [
            'notify_on_like',
            'notify_on_comment',
            'notify_on_new_follower',
            'notify_on_milestone',
        ]
