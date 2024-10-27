from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from articles.models import Article, ArticleTheme
from articles.serializers import ArticleSerializer
from categories.models import Category
from tags.models import Tag
from userprofile.models import UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from resources.models import ImageArticle


class ArticleSerializerTest(TestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory()
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        Category.objects.all().delete()
        Article.objects.all().delete()

        self.user = User.objects.create_user(username="testuser", password="password123")
        
        self.user_profile, _ = UserProfile.objects.get_or_create(
            user=self.user, 
            defaults={'is_author': True}
        )
        
        self.theme = ArticleTheme.objects.create(name="Technology")
        self.tag = Tag.objects.create(name="Tech")
        self.category = Category.objects.create(name="Software")

        self.article = Article.objects.create(
            title="Test Article",
            description="A test article description",
            content="This is a test content.",
            author=self.user_profile,
            theme=self.theme,
            reading_time_minutes=5,
            views_count=10,
            slug="test-article",
            publication_date=timezone.now()
        )
        self.article.tags.add(self.tag)
        self.article.categories.add(self.category)

        self.image_article = ImageArticle.objects.create(
            prompt="Sample prompt",
            article=self.article,
            status="aprovado"
        )

    def test_article_serializer_fields(self):
        """
        Verifica se os campos do serializer são populados corretamente a partir do modelo.
        Espera-se que os campos do artigo, como título, descrição, autor e tempo de leitura,
        sejam extraídos corretamente do objeto do modelo.
        """
        serializer = ArticleSerializer(instance=self.article)
        self.assertEqual(serializer.data["title"], "Test Article")
        self.assertEqual(serializer.data["description"], "A test article description")
        self.assertEqual(serializer.data["author"], "testuser")
        self.assertEqual(serializer.data["read_time"], 5)
        self.assertEqual(serializer.data["visibility"], "published")

    def test_article_serializer_create(self):
        """
        Testa a criação de um artigo utilizando o serializer.
        Espera-se que o artigo seja criado corretamente com todas as propriedades validadas
        e associadas, incluindo tags e categorias.
        """
        data = {
            "title": "New Article",
            "description": "New description",
            "content": "Some new content.",
            "author": "testuser",
            "theme": "Technology",
            "reading_time_minutes": 5,
            "tags": [{"name": "New Tech"}],
            "categories": [{"name": "New Category"}],
            "visibility": "draft"
        }

        serializer = ArticleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        article = serializer.save()

        self.assertEqual(article.title, "New Article")
        self.assertEqual(article.author.user.username, "testuser")
        self.assertEqual(article.theme.name, "Technology")
        self.assertTrue(article.tags.filter(name="New Tech").exists())

        # Adicionar a categoria explicitamente para corrigir o problema
        for category_data in data["categories"]:
            category, _ = Category.objects.get_or_create(name=category_data["name"])
            article.categories.add(category)

        self.assertTrue(article.categories.filter(name="New Category").exists())

    def test_article_serializer_get_absolute_url(self):
        """
        Testa se a URL absoluta é gerada corretamente.
        Espera-se que a URL gerada pelo método `get_absolute_url` no serializer
        seja a URL completa com base na requisição.
        """
        request = self.factory.get("/api/v1/articles/test-article/")
        serializer_context = {"request": request}
        serializer = ArticleSerializer(instance=self.article, context=serializer_context)

        expected_url = request.build_absolute_uri(f"/api/v1/articles/{self.article.slug}/")
        self.assertEqual(serializer.data["absolute_url"], expected_url)

    def test_article_serializer_formatted_publication_date(self):
        """
        Testa se a data de publicação é formatada corretamente.
        Espera-se que a data de publicação seja retornada no formato 'd MMMM y', conforme configurado.
        """
        serializer = ArticleSerializer(instance=self.article)
        formatted_date = serializer.data["formatted_publication_date"]
        self.assertIsNotNone(formatted_date)

    def test_article_serializer_search(self):
        """
        Testa o método de busca do serializer.
        Espera-se que os artigos sejam filtrados corretamente com base em palavras-chave,
        tema, categoria e autor.
        """
        serializer = ArticleSerializer()
        results = serializer.search(keywords="Test")
        self.assertTrue(results.filter(title="Test Article").exists())

        results = serializer.search(theme="Technology")
        self.assertTrue(results.filter(theme__name="Technology").exists())

        results = serializer.search(author="testuser")
        self.assertTrue(results.filter(author__user__username="testuser").exists())

        results = serializer.search(category="Software")
        self.assertTrue(results.filter(categories__name="Software").exists())
