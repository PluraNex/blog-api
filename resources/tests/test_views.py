from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from resources.models import ImageArticle
from articles.models import Article  # Presume que o modelo Article já existe


class ImageArticleListViewTest(TestCase):

    def setUp(self):
        """
        Configura o cliente de teste e cria artigos e artigos de imagem para os testes.
        """
        self.client = APIClient()
        self.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            content="Content of the test article"
        )
        ImageArticle.objects.create(
            prompt="Test prompt 1",
            article=self.article,
            status="aprovado"
        )
        ImageArticle.objects.create(
            prompt="Test prompt 2",
            article=self.article,
            status="em revisão"
        )
        # Ajuste o nome da URL para a lista de imagens
        self.list_url = reverse("image-article-list")  

    def test_list_image_articles(self):
        """
        Verifica se a `ImageArticleListView` retorna todos os artigos de imagem com status HTTP 200 OK.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["prompt"], "Test prompt 1")
        self.assertEqual(response.data[1]["prompt"], "Test prompt 2")


class ImageArticleDetailViewTest(TestCase):

    def setUp(self):
        """
        Configura o cliente de teste e cria um artigo e artigos de imagem para testes detalhados.
        """
        self.client = APIClient()
        self.article = Article.objects.create(
            title="Detail Article",
            slug="detail-article",
            content="Content of the detail article"
        )
        self.image_article = ImageArticle.objects.create(
            prompt="Detail prompt",
            article=self.article,
            status="não aprovado"
        )
        # Ajuste o nome da URL para o detalhe da imagem
        self.detail_url = reverse("image-article-detail", args=[self.image_article.id])

    def test_get_image_article_detail(self):
        """
        Verifica se a `ImageArticleDetailView` retorna os detalhes do artigo de imagem específico.
        Deve retornar HTTP 200 OK e incluir o campo `prompt` 'Detail prompt'.
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["prompt"], "Detail prompt")
        self.assertEqual(response.data["status"], "não aprovado")

    def test_get_image_article_detail_not_found(self):
        """
        Verifica se a `ImageArticleDetailView` retorna erro 404 quando o ID do artigo de imagem não existe.
        Deve retornar HTTP 404 NOT FOUND e uma mensagem de erro.
        """
        non_existent_url = reverse("image-article-detail", args=[9999])
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Image Article not found")
