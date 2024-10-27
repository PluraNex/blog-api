from django.test import TestCase
from django.utils.html import mark_safe
from resources.models import ImageArticle
from articles.models import Article  # Presume que você tem um modelo Article relacionado
from django.core.files.uploadedfile import SimpleUploadedFile

class ImageArticleModelTest(TestCase):

    def setUp(self):
        # Configura um artigo necessário para o relacionamento
        self.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            content="Content of the test article"
        )

    def test_image_article_creation(self):
        """
        Verifica a criação do `ImageArticle` e se os atributos são atribuídos corretamente.
        Deve retornar o prompt 'Test prompt', o status 'aprovado', e o `article_slug` 'test-article'.
        """
        image_article = ImageArticle.objects.create(
            prompt="Test prompt",
            article=self.article,
            status="aprovado"
        )
        self.assertEqual(image_article.prompt, "Test prompt")
        self.assertEqual(image_article.status, "aprovado")
        self.assertEqual(image_article.article_slug, "test-article")

    def test_save_method_sets_article_slug(self):
        """
        Verifica se o método `save` define o campo `article_slug` automaticamente se estiver vazio.
        Deve preencher `article_slug` com o slug do artigo, 'test-article'.
        """
        image_article = ImageArticle.objects.create(
            prompt="Another test prompt",
            article=self.article,
            article_slug="",  # Definido como vazio para testar a lógica de preenchimento
            status="em revisão"
        )
        image_article.save()
        self.assertEqual(image_article.article_slug, self.article.slug)

    def test_image_tag_with_image(self):
        """
        Verifica o método `image_tag` quando há uma imagem associada.
        Deve retornar o HTML com a imagem carregada e dimensões de 200x200px.
        """
        image = SimpleUploadedFile(name="test_image.jpg", content=b"", content_type="image/jpeg")
        image_article = ImageArticle.objects.create(
            prompt="Prompt with image",
            image=image,
            article=self.article
        )
        expected_html = mark_safe(
            f'<img src="{image_article.image.url}" style="max-width:200px; max-height:200px;" />'
        )
        self.assertEqual(image_article.image_tag(), expected_html)

    def test_image_tag_without_image(self):
        """
        Verifica o método `image_tag` quando não há imagem associada.
        Deve retornar a string 'Nenhuma imagem disponível'.
        """
        image_article = ImageArticle.objects.create(
            prompt="Prompt without image",
            article=self.article
        )
        self.assertEqual(image_article.image_tag(), "Nenhuma imagem disponível")

    def test_str_method(self):
        """
        Verifica a representação em string do `ImageArticle`.
        Deve retornar a string 'ImageArticle (não aprovado) for Test Article'.
        """
        image_article = ImageArticle.objects.create(
            prompt="String representation test",
            article=self.article,
            status="não aprovado"
        )
        self.assertEqual(
            str(image_article),
            f"ImageArticle (não aprovado) for {self.article}"
        )
