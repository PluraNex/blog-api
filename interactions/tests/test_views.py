# interactions/tests/test_views.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from interactions.models import InteractionType, UserInteraction
from interactions.tests.base_test import BaseInteractionTest
from rest_framework_simplejwt.tokens import RefreshToken


class InteractionViewTests(BaseInteractionTest, APITestCase):
    def setUp(self):
        super().setUp()
        
        # Autenticação JWT para o usuário principal
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_like_article(self):
        """
        Testa a criação de uma curtida em um artigo.
        Espera-se que o endpoint retorne 201 Created e que o contador de curtidas do artigo seja incrementado.
        """
        url = reverse("like-article", args=[self.article.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], f"You liked the article '{self.article.title}'")
        self.article.refresh_from_db()
        self.assertEqual(self.article.like_count, 1)

    def test_like_article_already_liked(self):
        """
        Testa a tentativa de curtir um artigo que já foi curtido pelo usuário.
        Espera-se que o endpoint retorne 400 Bad Request e uma mensagem indicando que o artigo já foi curtido.
        """
        UserInteraction.objects.create(
            user=self.user,
            content_object=self.article,
            interaction_type=InteractionType.LIKE
        )

        url = reverse("like-article", args=[self.article.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "You have already liked this article")

    def test_like_article_not_found(self):
        """
        Testa a tentativa de curtir um artigo inexistente.
        Espera-se que o endpoint retorne 404 Not Found com uma mensagem indicando que o artigo não foi encontrado.
        """
        url = reverse("like-article", args=[9999])  # ID inválido
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Article not found")

    def test_unlike_article(self):
        """
        Testa a remoção de uma curtida em um artigo.
        Espera-se que o endpoint retorne 200 OK e que o contador de curtidas do artigo seja decrementado.
        """
        UserInteraction.objects.create(
            user=self.user,
            content_object=self.article,
            interaction_type=InteractionType.LIKE
        )
        self.article.like_count = 1
        self.article.save()

        url = reverse("unlike-article", args=[self.article.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], f"You unliked the article '{self.article.title}'")
        self.article.refresh_from_db()
        self.assertEqual(self.article.like_count, 0)

    def test_unlike_article_not_liked(self):
        """
        Testa a tentativa de descurtir um artigo que não foi curtido pelo usuário.
        Espera-se que o endpoint retorne 400 Bad Request e uma mensagem indicando que o artigo não foi curtido.
        """
        url = reverse("unlike-article", args=[self.article.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "You have not liked this article")

    def test_follow_user(self):
        """
        Testa a criação de uma interação de seguir outro usuário.
        Espera-se que o endpoint retorne 201 Created e que o contador de seguidores do usuário seja incrementado.
        """
        url = reverse("follow-user", args=[self.other_user.username])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], f"You are now following {self.other_user.username}")
        self.other_profile.refresh_from_db()
        self.assertEqual(self.other_profile.follow_count, 1)

    def test_follow_user_already_following(self):
        """
        Testa a tentativa de seguir um usuário que já está sendo seguido.
        Espera-se que o endpoint retorne 400 Bad Request com uma mensagem indicando que o usuário já está sendo seguido.
        """
        UserInteraction.objects.create(
            user=self.user,
            content_object=self.other_profile,
            interaction_type=InteractionType.FOLLOW
        )

        url = reverse("follow-user", args=[self.other_user.username])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "You are already following this user")

    def test_follow_user_not_found(self):
        """
        Testa a tentativa de seguir um usuário inexistente.
        Espera-se que o endpoint retorne 404 Not Found com uma mensagem de erro.
        """
        url = reverse("follow-user", args=["nonexistentuser"])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User not found")

    def test_unfollow_user(self):
        """
        Testa a remoção de uma interação de seguir um usuário.
        Espera-se que o endpoint retorne 200 OK e que o contador de seguidores do usuário seja decrementado.
        """
        UserInteraction.objects.create(
            user=self.user,
            content_object=self.other_profile,
            interaction_type=InteractionType.FOLLOW
        )
        self.other_profile.follow_count = 1
        self.other_profile.save()

        url = reverse("unfollow-user", args=[self.other_user.username])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], f"You have unfollowed {self.other_user.username}")
        self.other_profile.refresh_from_db()
        self.assertEqual(self.other_profile.follow_count, 0)

    def test_unfollow_user_not_following(self):
        """
        Testa a tentativa de deixar de seguir um usuário que não está sendo seguido.
        Espera-se que o endpoint retorne 400 Bad Request com uma mensagem indicando que o usuário não está sendo seguido.
        """
        url = reverse("unfollow-user", args=[self.other_user.username])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "You are not following this user")

    def test_follow_self(self):
        """
        Testa a tentativa de seguir a si mesmo.
        Espera-se que o endpoint retorne 400 Bad Request com uma mensagem indicando que o usuário não pode seguir a si próprio.
        """
        url = reverse("follow-user", args=[self.user.username])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "You cannot follow yourself")
