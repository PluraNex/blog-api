from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from authors.models import Author
from authors.serializers import AuthorSerializer

class AuthorDetailViewTest(APITestCase):

    def setUp(self):
        # Criação do autor de teste
        self.author = Author.objects.create(
            name="John Doe",
            biography="A passionate author.",
            profession="Writer"
        )
        self.valid_url = reverse('author-detail', args=[self.author.id])
        self.invalid_url = reverse('author-detail', args=[9999])  # ID inexistente

    def test_should_return_author_details_when_author_exists(self):
        """
        Verifica se a API retorna os detalhes corretos do autor existente.
        """
        response = self.client.get(self.valid_url)
        expected_data = AuthorSerializer(self.author).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_should_return_404_when_author_does_not_exist(self):
        """
        Verifica se a API retorna um erro 404 para um autor inexistente.
        """
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
