from django.test import TestCase
from django.utils.text import slugify
from articles.models import Article, ArticleTheme
from userprofile.models import UserProfile
from categories.models import Category
from tags.models import Tag
from resources.models import ImageArticle
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class ArticleModelTest(TestCase):
    
    def setUp(self):
        # Limpar dados anteriores
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        Category.objects.all().delete()
        Article.objects.all().delete()

        self.user = User.objects.create_user(username="testuser", password="password123")
        
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user, 
            defaults={'is_author': True}
        )

        # Criando outros objetos necessários para os testes
        self.theme = ArticleTheme.objects.create(name="Technology")
        self.tag = Tag.objects.create(name="Tech")
        self.category = Category.objects.create(name="Software")

        # Criando um artigo para associar ao ImageArticle
        self.article = Article.objects.create(
            title="Sample Article",
            content="Content for sample article.",
            author=self.user_profile
        )

        # Ajuste para `ImageArticle` com campos válidos
        self.image_article = ImageArticle.objects.create(
            prompt="Sample prompt",
            article=self.article,
            status="aprovado"
        )

    def test_article_creation(self):
        """
        Verifica se um artigo é criado corretamente e salvo no banco de dados.
        Espera-se que um artigo chamado 'Introduction to Django' seja criado e que as propriedades sejam atribuídas corretamente.
        Também verifica se o slug é gerado corretamente e se a URL está no formato esperado.
        """
        article = Article.objects.create(
            title="Introduction to Django",
            description="Learn the basics of Django",
            content="Django is a high-level Python Web framework...",
            author=self.user_profile,
            theme=self.theme,
            reading_time_minutes=10,
            image_article=self.image_article,
            visibility="published"
        )
        article.tags.add(self.tag)
        article.categories.add(self.category)

        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(article.title, "Introduction to Django")
        self.assertEqual(article.slug, slugify("Introduction to Django"))
        self.assertEqual(article.get_absolute_url(), f"/api/v1/articles/{article.slug}/")
        self.assertEqual(article.visibility, "published")
        self.assertEqual(str(article), "Introduction to Django")



    def test_article_slug_generation(self):
        """
        Verifica se o slug é gerado automaticamente ao salvar o artigo.
        Espera-se que o slug seja uma versão 'slugificada' do título do artigo.
        """
        article = Article.objects.create(
            title="Learn Python Programming",
            content="Content for Python article...",
            author=self.user_profile
        )
        self.assertEqual(article.slug, slugify("Learn Python Programming"))

    def test_article_slug_uniqueness(self):
        """
        Verifica se dois artigos não podem ter o mesmo slug.
        Espera-se que uma exceção seja levantada ao tentar criar dois artigos com o mesmo título,
        garantindo que o slug gerado seja único.
        """
        Article.objects.create(
            title="Same Title",
            content="Content 1",
            author=self.user_profile
        )
        with self.assertRaises(Exception):
            Article.objects.create(
                title="Same Title",
                content="Content 2",
                author=self.user_profile
            )

    def test_article_reading_time_validator(self):
        """
        Verifica se o validador de tempo de leitura não permite valores abaixo de 1.
        Espera-se que uma exceção seja levantada ao tentar definir reading_time_minutes como 0.
        """
        article = Article(
            title="Invalid Reading Time",
            content="Content...",
            reading_time_minutes=0,
            author=self.user_profile
        )
        # Valida explicitamente o modelo antes de salvar para acionar o validador
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_article_string_representation(self):
        """
        Verifica se a representação em string de um artigo retorna o título corretamente.
        Espera-se que a representação de um artigo 'Test Article' retorne 'Test Article'.
        """
        article = Article.objects.create(
            title="Test Article",
            content="Just a test",
            author=self.user_profile
        )
        self.assertEqual(str(article), "Test Article")

    def test_article_update_views_count(self):
        """
        Verifica se a contagem de visualizações é atualizada corretamente.
        Espera-se que o contador de views aumente de 10 para 11 após a atualização.
        """
        article = Article.objects.create(
            title="Popular Article",
            content="Content about popularity",
            views_count=10,
            author=self.user_profile
        )
        article.views_count += 1
        article.save()

        updated_article = Article.objects.get(id=article.id)
        self.assertEqual(updated_article.views_count, 11)

    def test_article_versioning(self):
        """
        Verifica se a versão do artigo pode ser incrementada corretamente.
        Espera-se que, após atualizar a versão de 1 para 2, o valor refletido seja 2.
        """
        article = Article.objects.create(
            title="Version Control",
            content="Version test content",
            version=1,
            author=self.user_profile
        )
        article.version += 1
        article.save()

        updated_article = Article.objects.get(id=article.id)
        self.assertEqual(updated_article.version, 2)
