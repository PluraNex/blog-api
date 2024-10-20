from django.test import TestCase
from authors.models import Author
from authors.serializers import AuthorSerializer

class AuthorSerializerTest(TestCase):

    def setUp(self):
        self.author_attributes = {
            "name": "Jane Doe",
            "biography": "An insightful writer.",
            "profession": "Journalist",
            "image": None
        }

        self.author = Author.objects.create(**self.author_attributes)
        self.serializer = AuthorSerializer(instance=self.author)

    def test_contains_expected_fields(self):
        """
        Testa se o serializer contém os campos esperados.
        """
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(["id", "name", "biography", "profession", "image"]))

    def test_field_content(self):
        """
        Testa se o conteúdo dos campos serializados está correto.
        """
        data = self.serializer.data
        self.assertEqual(data["name"], self.author_attributes["name"])
        self.assertEqual(data["biography"], self.author_attributes["biography"])
        self.assertEqual(data["profession"], self.author_attributes["profession"])
        self.assertEqual(data["image"], self.author_attributes["image"])

    def test_valid_serialization(self):
        """
        Testa se a desserialização e validação do serializer funcionam corretamente.
        """
        valid_data = {
            "name": "Alice Smith",
            "biography": "A skilled author.",
            "profession": "Editor",
            "image": None
        }
        serializer = AuthorSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], valid_data["name"])

    def test_invalid_serialization(self):
        """
        Testa se o serializer lida corretamente com dados inválidos.
        """
        invalid_data = {
            "name": "",  # Nome vazio, deve falhar
            "biography": "This author lacks a valid name.",
            "profession": "Novelist"
        }
        serializer = AuthorSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
