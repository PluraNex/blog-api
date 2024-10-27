from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from categories.models import Category
from articles.models import Article
from userprofile.models import UserProfile
from django.contrib.auth.models import User

class CategoryViewTest(TestCase):
    BASE_URL = "/api/v1/categories/"

    def setUp(self):
        """
        Cria uma instância de cliente e configura uma categoria com artigos associados
        para serem utilizados nos testes das views. Inclui criação de usuário e perfil de autor.
        """
        self.client = APIClient()

        # Limpar dados anteriores
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        Category.objects.all().delete()
        Article.objects.all().delete()

        self.user = User.objects.create_user(username="testuser", password="password123")
        
        self.user_profile, _ = UserProfile.objects.get_or_create(
            user=self.user, 
            defaults={'is_author': True}
        )

        self.category = Category.objects.create(name="Technology")
        self.article1 = Article.objects.create(
            title="Tech News",
            content="Latest updates on tech",
            author=self.user_profile,
        )
        self.article2 = Article.objects.create(
            title="AI Advancements",
            content="Deep learning trends",
            author=self.user_profile,
        )

        self.category.articles.set([self.article1, self.article2])
        self.category.save()

    # Listar categorias
    def test_get_all_categories(self):
        """
        Verifica se a listagem de categorias retorna o status HTTP 200 OK.
        Deve incluir todas as categorias disponíveis e o número correto de artigos associados.
        """
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Technology")

    def test_category_list_no_categories(self):
        """
        Verifica se a listagem de categorias retorna uma lista vazia quando não há categorias disponíveis.
        Deve retornar HTTP 200 OK e um array vazio.
        """
        Category.objects.all().delete()  # Remove todas as categorias existentes
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # Detalhes de categoria
    def test_get_category_detail(self):
        """
        Verifica se os artigos associados a uma categoria são retornados corretamente.
        Deve retornar HTTP 200 OK e uma lista paginada de artigos relacionados à categoria especificada.
        """
        response = self.client.get(reverse("category-detail", args=[self.category.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_category_not_found(self):
        """
        Verifica se uma tentativa de buscar uma categoria inexistente retorna HTTP 404 NOT FOUND.
        Deve exibir uma mensagem de erro indicando que a categoria não foi encontrada.
        """
        response = self.client.get(reverse("category-detail", args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Category not found")

    def test_category_detail_page_no_articles(self):
        """
        Verifica se acessar uma categoria sem artigos retorna uma lista vazia.
        Deve retornar HTTP 200 OK e um array vazio.
        """
        # Cria uma nova categoria sem artigos associados
        new_category = Category.objects.create(name="Empty Category")
        response = self.client.get(f"{self.BASE_URL}{new_category.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    # Testes de paginação
    def test_category_pagination_out_of_range(self):
        """
        Verifica se uma página que excede o número total de páginas retorna uma lista vazia.
        Deve retornar HTTP 200 OK e nenhum artigo.
        """
        response = self.client.get(f"{self.BASE_URL}{self.category.id}/?page=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], 2)

    def test_category_pagination_invalid_page(self):
        """
        Verifica se uma página inválida (não um número inteiro) retorna a primeira página como fallback.
        Deve retornar HTTP 200 OK e os artigos na primeira página.
        """
        response = self.client.get(f"{self.BASE_URL}{self.category.id}/?page=abc")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_pagination_first_page(self):
        """
        Verifica se na primeira página `previous` é None e `next` não é None quando há múltiplas páginas.
        Deve retornar HTTP 200 OK, previous como None e next como uma URL válida.
        """
        response = self.client.get(f"{self.BASE_URL}{self.category.id}/?page_size=1")
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
        self.category.articles.add(article3)
        response = self.client.get(f"{self.BASE_URL}{self.category.id}/?page=2&page_size=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["previous"])
        self.assertIsNotNone(response.data["next"])
    
    def test_articles_order(self):
        """
        Verifica se os artigos são retornados na ordem correta de criação.
        """
        response = self.client.get(reverse("category-detail", args=[self.category.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["results"][0]['publication_date'], response.data["results"][1]['publication_date'])
