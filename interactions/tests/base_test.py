# interactions/tests/base_test.py

from django.test import TestCase
from interactions.models import UserInteraction, InteractionType
from userprofile.models import UserProfile
from articles.models import Article
from django.contrib.auth.models import User

class BaseInteractionTest(TestCase):
    def setUp(self):
        """
        Configuração comum para testes de interações.
        """
        # Limpeza inicial dos dados
        self.clear_previous_data()

        # Criação de um usuário principal e perfil
        self.user, _ = User.objects.get_or_create(username="testuser", password="password123")
        self.user_profile, _ = UserProfile.objects.get_or_create(user=self.user, defaults={'is_author': True})

        # Criação de um segundo usuário e perfil para follow/unfollow
        self.other_user, _ = User.objects.get_or_create(username="otheruser", password="password123")
        self.other_profile, _ = UserProfile.objects.get_or_create(user=self.other_user)

        # Criação de um artigo associado ao perfil do usuário principal
        self.article, _ = Article.objects.get_or_create(
            title="Test Article",
            content="Content of the test article",
            author=self.user_profile
        )

    def tearDown(self):
        """
        Limpa todos os dados de teste após cada execução.
        """
        self.clear_previous_data()

    def clear_previous_data(self):
        UserInteraction.objects.all().delete()
        Article.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
