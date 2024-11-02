# user_preferences/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from userprofile.models import UserProfile
from .models import NotificationSettings

@receiver(post_save, sender=UserProfile)
def create_notification_settings(sender, instance, created, **kwargs):
    if created:
        NotificationSettings.objects.create(user_profile=instance)
