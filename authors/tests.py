from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from authors.models import Author
from authors.serializers import AuthorSerializer

class AuthorDetailViewTest(APITestCase):

    def setUp(self):
        # Cria um autor para usar nos testes
        self.author = Author.objects.create(
            name="John Doe",
            biography="A passionate author.",
            profession="Writer"
        )
        self.valid_url = reverse('author-detail', args=[self.author.id])
        self.invalid_url = reverse('author-detail', args=[9999])  # ID que não existe

    def test_get_author_details(self):
        """
        Testa se os detalhes do autor são retornados corretamente.
        """
        response = self.client.get(self.valid_url)
        expected_data = AuthorSerializer(self.author).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_nonexistent_author(self):
        """
        Testa se a resposta correta é retornada para um autor inexistente.
        """
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Author not found"})
