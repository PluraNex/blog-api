from django.test import TestCase
from django.contrib.auth.models import User
from userprofile.serializers import UserProfileSerializer
from userprofile.models import UserProfile

class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profile = self.user.userprofile
        self.profile.bio = "Test Bio"
        self.profile.location = "Test Location"
        self.profile.gender = "M"
        self.profile.save()

    def test_userprofile_serializer(self):
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data

        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['bio'], "Test Bio")
        self.assertEqual(data['location'], "Test Location")
        self.assertEqual(data['gender'], "M")

    def test_userprofile_serializer_update(self):
        serializer = UserProfileSerializer(instance=self.profile, data={
            "bio": "New Bio",
            "location": "New Location"
        }, partial=True)

        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()

        self.assertEqual(updated_profile.bio, "New Bio")
        self.assertEqual(updated_profile.location, "New Location")
