# user_preferences/models.py
from django.db import models
from userprofile.models import UserProfile

class NotificationSettings(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="notification_settings")
    
    notify_on_like = models.BooleanField(default=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_new_follower = models.BooleanField(default=True)
    notify_on_milestone = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification settings for {self.user_profile.user.username}"
