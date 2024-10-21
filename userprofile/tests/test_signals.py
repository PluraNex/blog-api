# userprofile/tests/test_signals.py
from django.test import TestCase
from django.contrib.auth.models import User
from userprofile.models import UserProfile

class UserProfileSignalTest(TestCase):
    
    def test_create_user_creates_profile(self):
        user = User.objects.create(username="testuser", email="testuser@example.com")
       
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_update_user_updates_profile(self):
        user = User.objects.create(username="testuser2", email="testuser2@example.com")
        user.username = "newusername"
        user.save()

        self.assertEqual(user.userprofile.user.username, "newusername")
