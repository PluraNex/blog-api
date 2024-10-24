from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from tags.models import Tag
from articles.models import Article
from userprofile.models import UserProfile
from django.contrib.auth.models import User

class TagViewTest(TestCase):
    BASE_URL = "/api/v1/tags/"

    def setUp(self):
        """
        Cria uma instância de cliente e configura uma tag com artigos associados
        para serem utilizados nos testes das views. Inclui criação de usuário e perfil de autor.
        """
        self.client = APIClient()

        User.objects.all().delete()
        UserProfile.objects.all().delete()
        Tag.objects.all().delete()
        Article.objects.all().delete()

        self.user = User.objects.create_user(username="testuser", password="password123")
        
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user, 
            defaults={'is_author': True}
        )

        self.tag = Tag.objects.create(name="Technology")
        self.article1 = Article.objects.create(
            title="Tech News",
            content="Latest updates on tech",
            author=self.user_profile,  # Associar o autor ao artigo
        )
        self.article2 = Article.objects.create(
            title="AI Advancements",
            content="Deep learning trends",
            author=self.user_profile,  # Associar o autor ao artigo
        )

        self.tag.articles.set([self.article1, self.article2])
        self.tag.save()

    def test_get_all_tags(self):
        """
        Verifica se a listagem de tags retorna o status HTTP 200 OK.
        Deve incluir todas as tags disponíveis e o número correto de artigos associados.
        """
        response = self.client.get(reverse("tag-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Technology")

    def test_get_tag_detail(self):
        """
        Verifica se os artigos associados a uma tag são retornados corretamente.
        Deve retornar HTTP 200 OK e uma lista paginada de artigos relacionados à tag especificada.
        """
        response = self.client.get(reverse("tag-detail", args=[self.tag.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_tag_not_found(self):
        """
        Verifica se uma tentativa de buscar uma tag inexistente retorna HTTP 404 NOT FOUND.
        Deve exibir uma mensagem de erro indicando que a tag não foi encontrada.
        """
        response = self.client.get(reverse("tag-detail", args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Tag not found")
    
    def test_tag_pagination_invalid_page(self):
        """
        Verifica se uma página inválida (não um número inteiro) retorna a primeira página como fallback.
        Deve retornar HTTP 200 OK e os artigos na primeira página.
        """
        response = self.client.get(f"{self.BASE_URL}{self.tag.id}/?page=abc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_tag_pagination_out_of_range(self):
        """
        Verifica se uma página que excede o número total de páginas retorna uma lista vazia.
        Deve retornar HTTP 200 OK e nenhum artigo.
        """
        response = self.client.get(f"{self.BASE_URL}{self.tag.id}/?page=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], 2)

    def test_tag_pagination_custom_page_size(self):
        """
        Verifica se definir um 'page_size' personalizado funciona corretamente.
        Deve retornar HTTP 200 OK e a quantidade correta de artigos por página.
        """
        response = self.client.get(f"{self.BASE_URL}{self.tag.id}/?page_size=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_pagination_first_page(self):
        """
        Verifica se na primeira página `previous` é None e `next` não é None quando há múltiplas páginas.
        Deve retornar HTTP 200 OK, previous como None e next como uma URL válida.
        """
        response = self.client.get(f"{self.BASE_URL}{self.tag.id}/?page_size=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["previous"])
        self.assertIsNotNone(response.data["next"])

    def test_pagination_middle_page(self):
        """
        Verifica se em uma página intermediária `previous` e `next` não são None.
        Deve retornar HTTP 200 OK, previous e next como URLs válidas.
        """

        article3 = Article.objects.create(
            title="New Tech Trends",
            content="Interesting developments in tech",
            author=self.user_profile
        )
        self.tag.articles.add(article3)

        response = self.client.get(f"{self.BASE_URL}{self.tag.id}/?page=2&page_size=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["previous"])
        self.assertIsNotNone(response.data["next"])
