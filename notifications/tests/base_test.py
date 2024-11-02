# notifications/tests/base_test.py
from django.test import TestCase
from notifications.models import NotificationInteraction
from userprofile.models import UserProfile
from articles.models import Article
from user_preferences.models import NotificationSettings
from django.contrib.auth.models import User

class BaseNotificationTest(TestCase):
    def setUp(self):
        """
        Configuração comum para testes de notificações e serialização.
        Cria um usuário, perfil, configurações de notificação e um artigo.
        """
        # Limpeza inicial
        self.clear_previous_data()

        # Configuração do usuário e perfil
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.user_profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.user_profile.is_author = True
        self.user_profile.save()

        # Configurações de notificação para o autor
        self.notification_settings, _ = NotificationSettings.objects.get_or_create(user_profile=self.user_profile)

        # Criação de um artigo pelo autor
        self.article = Article.objects.create(
            title="Test Article",
            content="Content of the test article",
            author=self.user_profile
        )

        # Criação de uma notificação de exemplo para uso em testes de serialização
        self.notification = NotificationInteraction.objects.create(
            user=self.user,
            message="Test notification message",
            interaction_type="LIKE"
        )

    def tearDown(self):
        """
        Limpa todos os dados de teste após cada execução.
        """
        self.clear_previous_data()

    def clear_previous_data(self):
        """
        Limpa dados de usuários, perfis, configurações, notificações e artigos.
        """
        NotificationInteraction.objects.all().delete()
        NotificationSettings.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        Article.objects.all().delete()
