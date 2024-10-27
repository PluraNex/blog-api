from django.test import TestCase
from tags.models import Tag

class TagModelTest(TestCase):
    
    def setUp(self):
        self.tag = Tag.objects.create(name="Test Tag")
    
    def test_tag_creation(self):
        """
        Verifica se o modelo Tag é criado corretamente.
        Deve armazenar o nome da tag e retornar a representação correta em string.
        """
        self.assertEqual(self.tag.name, "Test Tag")
        self.assertEqual(str(self.tag), "Test Tag")
