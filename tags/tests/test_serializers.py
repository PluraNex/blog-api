from django.test import TestCase
from tags.models import Tag
from tags.serializers import TagSerializer

class TagSerializerTest(TestCase):
    
    def setUp(self):
        self.tag = Tag.objects.create(name="Sample Tag")

    def test_tag_serializer(self):
        """
        Verifica se o serializer converte o objeto Tag corretamente.
        Deve retornar o nome da tag e incluir o campo 'article_count' inicializado em 0.
        """
        serializer = TagSerializer(self.tag)
        data = serializer.data
        self.assertEqual(data["name"], "Sample Tag")
        self.assertEqual(data["article_count"], 0)
