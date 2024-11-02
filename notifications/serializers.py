# notifications/serializers.py
from rest_framework import serializers
from .models import NotificationInteraction

class NotificationInteractionSerializer(serializers.ModelSerializer):
    object_id = serializers.IntegerField(source='content_object.id', read_only=True)
    object_type = serializers.CharField(source='content_type.model', read_only=True)
    origin_user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = NotificationInteraction
        fields = ['id', 'message', 'read', 'interaction_type', 'created_at', 'object_id', 'object_type', 'origin_user']
