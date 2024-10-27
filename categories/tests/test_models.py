from django.test import TestCase
from categories.models import Category

class CategoryModelTest(TestCase):

    def test_create_category(self):
        """
        Verifica se uma categoria pode ser criada corretamente e salva no banco de dados.
        Espera-se que uma categoria chamada 'Technology' seja criada e esteja disponível no banco.
        """
        category = Category.objects.create(name="Technology")
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(category.name, "Technology")

    def test_category_name_uniqueness(self):
        """
        Verifica se duas categorias não podem ter o mesmo nome (unique constraint).
        Espera-se que uma exceção seja levantada ao tentar criar duas categorias com o nome 'Science'.
        """
        Category.objects.create(name="Science")
        with self.assertRaises(Exception):
            Category.objects.create(name="Science")

    def test_category_string_representation(self):
        """
        Verifica se a representação em string de uma categoria retorna o nome corretamente.
        Espera-se que a representação em string de uma categoria 'Health' retorne 'Health'.
        """
        category = Category.objects.create(name="Health")
        self.assertEqual(str(category), "Health")

    def test_category_name_max_length(self):
        """
        Verifica se uma exceção é levantada ao tentar criar uma categoria com um nome que excede o tamanho máximo permitido.
        Espera-se que criar um nome com mais de 50 caracteres levante uma exceção.
        """
        long_name = "A" * 51  # Nome com mais de 50 caracteres
        with self.assertRaises(Exception):
            Category.objects.create(name=long_name)
