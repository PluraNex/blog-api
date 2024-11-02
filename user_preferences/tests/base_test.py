# user_preferences/tests/base_test.py
from django.test import TestCase
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from user_preferences.models import NotificationSettings

class BaseTestSetup(TestCase):
    
    def setUp(self):
        """
        Limpa dados anteriores e cria objetos necessários para os testes.
        """
        self.clear_previous_data()
        self.create_test_user_and_settings()

    def tearDown(self):
        """
        Limpa todos os dados de teste após cada teste.
        """
        self.clear_previous_data()

    def clear_previous_data(self):
        """
        Limpa dados anteriores de usuários, perfis de usuário e configurações de notificação.
        """
        NotificationSettings.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def create_test_user_and_settings(self):
        """
        Cria um usuário, perfil de usuário e configurações de notificação para uso nos testes.
        """
        self.user, _ = User.objects.get_or_create(username='testuser', defaults={'password': 'test_password'})
        self.user_profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.notification_settings, _ = NotificationSettings.objects.get_or_create(user_profile=self.user_profile)
