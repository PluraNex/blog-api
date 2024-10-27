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
        """
        Limpar dados anteriores e criar objetos necessários para os testes.
        """
        self.clear_previous_data()
        self.create_test_user()
        self.create_common_objects()

    def clear_previous_data(self):
        """
        Limpa dados anteriores de usuários, perfis de usuários, categorias e artigos.
        """
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        Category.objects.all().delete()
        Article.objects.all().delete()

    def create_test_user(self):
        """
        Cria um usuário e um perfil de autor para uso nos testes.
        """
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.user_profile, _ = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={'is_author': True}
        )

    def create_common_objects(self):
        """
        Cria objetos comuns usados nos testes, como tema, tag, categoria, artigo e imagem do artigo.
        """
        self.theme = ArticleTheme.objects.create(name="Technology")
        self.tag = Tag.objects.create(name="Tech")
        self.category = Category.objects.create(name="Software")
        self.article = Article.objects.create(
            title="Sample Article",
            content="Content for sample article.",
            author=self.user_profile,
            theme=self.theme
        )
        self.image_article = ImageArticle.objects.create(
            prompt="Sample prompt",
            article=self.article,
            status="aprovado"
        )

    def create_article(self, **kwargs):
        """
        Função auxiliar para criar artigos adicionais com o autor de teste.
        """
        return Article.objects.create(author=self.user_profile, **kwargs)

    def test_article_creation(self):
        """
        Testa a criação de um artigo e verifica se todas as propriedades são atribuídas corretamente.
        Espera-se que o artigo 'Introduction to Django' seja criado, com slug gerado automaticamente,
        URL correta e visibilidade definida como 'published'.
        """
        article = self.create_article(
            title="Introduction to Django",
            description="Learn the basics of Django",
            content="Django is a high-level Python Web framework...",
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
        self.assertEqual(article.visibility, "published")
        self.assertEqual(str(article), "Introduction to Django")

    def test_article_slug_generation(self):
        """
        Testa a geração automática do slug ao salvar o artigo.
        Espera-se que o slug seja uma versão 'slugificada' do título do artigo.
        """
        article = self.create_article(
            title="Learn Python Programming",
            content="Content for Python article..."
        )
        self.assertEqual(article.slug, slugify("Learn Python Programming"))

    def test_article_slug_preservation(self):
        """
        Verifica se o slug é preservado ao salvar novamente o artigo.
        Espera-se que o slug não mude quando o título é alterado após a criação do artigo.
        """
        article = self.create_article(
            title="Persistent Slug",
            content="Slug should not change.",
        )
        original_slug = article.slug
        article.title = "Updated Title"
        article.save()

        self.assertEqual(article.slug, original_slug)

    def test_article_slug_uniqueness(self):
        """
        Testa a unicidade do slug para garantir que dois artigos não possam ter o mesmo slug.
        Espera-se que uma exceção seja levantada ao tentar criar dois artigos com o mesmo título,
        garantindo que o slug gerado seja único.
        """
        self.create_article(title="Unique Slug", content="Content 1")
        with self.assertRaises(Exception):
            self.create_article(title="Unique Slug", content="Content 2")

    def test_article_reading_time_validator(self):
        """
        Verifica se o validador de tempo de leitura não permite valores abaixo de 1.
        Espera-se que uma exceção seja levantada ao tentar definir reading_time_minutes como 0.
        """
        article = self.create_article(
            title="Invalid Reading Time",
            content="Content...",
            reading_time_minutes=0
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_article_string_representation(self):
        """
        Testa a representação em string de um artigo.
        Espera-se que a representação de um artigo com título 'Test Article' retorne 'Test Article'.
        """
        article = self.create_article(
            title="Test Article",
            content="Just a test"
        )
        self.assertEqual(str(article), "Test Article")

    def test_article_update_views_count(self):
        """
        Verifica se a contagem de visualizações é atualizada corretamente.
        Espera-se que o contador de views aumente de 10 para 11 após a atualização.
        """
        article = self.create_article(
            title="Popular Article",
            content="Content about popularity",
            views_count=10
        )
        article.views_count += 1
        article.save()
        updated_article = Article.objects.get(id=article.id)
        self.assertEqual(updated_article.views_count, 11)

    def test_article_versioning(self):
        """
        Testa se a versão do artigo pode ser incrementada corretamente.
        Espera-se que, após atualizar a versão de 1 para 2, o valor refletido seja 2.
        """
        article = self.create_article(
            title="Version Control",
            content="Version test content",
            version=1
        )
        article.version += 1
        article.save()
        updated_article = Article.objects.get(id=article.id)
        self.assertEqual(updated_article.version, 2)
