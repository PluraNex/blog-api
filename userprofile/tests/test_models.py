from django.test import TestCase
from django.contrib.auth.models import User

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profile = self.user.userprofile

    def test_userprofile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, "")
        self.assertEqual(self.profile.location, "")
        self.assertEqual(str(self.profile), "testuser Profile")
