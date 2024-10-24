from django.test import TestCase
from categories.models import Category
from categories.serializers import CategorySerializer

class CategorySerializerTest(TestCase):

    def test_valid_category_serialization(self):
        """
        Verifica se uma categoria válida é serializada corretamente.
        Espera-se que uma categoria com nome 'Music' seja convertida em um dicionário contendo 'id' e 'name'.
        """
        category = Category.objects.create(name="Music")
        serializer = CategorySerializer(category)
        expected_data = {
            "id": category.id,
            "name": "Music"
        }
        self.assertEqual(serializer.data, expected_data)

    def test_valid_category_deserialization(self):
        """
        Verifica se os dados válidos são deserializados e criam uma nova categoria corretamente.
        Espera-se que os dados com o nome 'Art' sejam validados e a categoria seja salva no banco.
        """
        data = {"name": "Art"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        category = serializer.save()
        self.assertEqual(category.name, "Art")

    def test_invalid_category_deserialization(self):
        """
        Verifica se os dados inválidos (exemplo: nome em branco) não são considerados válidos.
        Espera-se que dados com um nome vazio sejam considerados inválidos e gerem um erro de validação.
        """
        data = {"name": ""}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_category_name_uniqueness_validation(self):
        """
        Verifica se a validação de unicidade do nome da categoria é aplicada durante a desserialização.
        Espera-se que tentar criar uma categoria com um nome já existente ('Education') retorne um erro de validação.
        """
        Category.objects.create(name="Education")
        data = {"name": "Education"}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
