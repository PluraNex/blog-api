from django.test import TestCase
from authors.models import Author

class AuthorModelTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            name="John Doe",
            biography="A passionate author.",
            profession="Writer"
        )

    def test_author_str_method(self):
        """
        Testa se o método __str__ do modelo Author retorna o nome corretamente.
        """
        self.assertEqual(str(self.author), "John Doe")
