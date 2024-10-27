from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from resources.models import ImageArticle
from articles.models import Article
from resources.serializers import ImageArticleSerializer


class ImageArticleSerializerTest(TestCase):

    def setUp(self):
        """
        Configura um artigo e um artigo de imagem para testar o serializer.
        """
        self.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            content="Content of the test article"
        )
        self.image_article = ImageArticle.objects.create(
            prompt="Test prompt",
            article=self.article,
            status="aprovado"
        )

    def test_image_article_serializer_data(self):
        """
        Verifica se o `ImageArticleSerializer` serializa os dados corretamente.
        Deve incluir todos os campos: `prompt`, `image_url`, `article_title`, `status`, `article_slug`, `created_at` e `updated_at`.
        """
        serializer = ImageArticleSerializer(instance=self.image_article)
        data = serializer.data
        self.assertEqual(data["prompt"], self.image_article.prompt)
        self.assertEqual(data["status"], self.image_article.status)
        self.assertEqual(data["article_title"], self.article.title)
        self.assertEqual(data["article_slug"], self.article.slug)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("image_url", data)

    def test_image_url_field_with_image(self):
        """
        Verifica se o campo `image_url` é serializado corretamente quando uma imagem está presente.
        Deve retornar a URL da imagem em `image_url` quando a imagem está disponível.
        """
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.image_article.image = image
        self.image_article.save()

        serializer = ImageArticleSerializer(instance=self.image_article)
        data = serializer.data
        self.assertIn("image_url", data)
        self.assertIsNotNone(data["image_url"])  # `image_url` deve conter a URL da imagem.

    def test_image_url_field_without_image(self):
        """
        Verifica se o campo `image_url` é `null` quando nenhuma imagem está presente.
        Deve retornar `null` em `image_url` quando não há imagem associada.
        """
        serializer = ImageArticleSerializer(instance=self.image_article)
        data = serializer.data
        self.assertIn("image_url", data)
        self.assertIsNone(data["image_url"])  # `image_url` deve ser `null` quando não há imagem.

    def test_read_only_fields(self):
        """
        Verifica se os campos `article_slug`, `created_at`, `updated_at`, e `article_title` são declarados como somente leitura
        no `ImageArticleSerializer`.
        Deve retornar esses campos como somente leitura, impedindo alterações diretas.
        """
        serializer = ImageArticleSerializer()
        read_only_fields = serializer.Meta.read_only_fields

        self.assertIn("article_slug", read_only_fields)
        self.assertIn("created_at", read_only_fields)
        self.assertIn("updated_at", read_only_fields)
        self.assertNotIn("article_title", read_only_fields)  # `article_title` não faz parte do `read_only_fields` na Meta

    def test_update_with_read_only_fields(self):
        """
        Verifica se ao tentar atualizar um artigo de imagem, os campos de somente leitura permanecem inalterados.
        Deve manter `article_slug` e `article_title` com seus valores originais após atualização parcial.
        """
        update_data = {
            "prompt": "Updated prompt",
            "status": "em revisão",
            "article_slug": "new-article-slug",
            "article_title": "New Title"
        }
        serializer = ImageArticleSerializer(instance=self.image_article, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_image_article = serializer.save()

        self.assertEqual(updated_image_article.prompt, update_data["prompt"])
        self.assertEqual(updated_image_article.status, update_data["status"])

        # Campos de somente leitura devem permanecer inalterados
        self.assertEqual(updated_image_article.article_slug, self.article.slug)
        self.assertEqual(updated_image_article.article.title, self.article.title)

    def test_partial_update_prompt_only(self):
        """
        Verifica se o `ImageArticleSerializer` permite atualização parcial do campo `prompt`.
        Deve atualizar apenas o campo `prompt`, mantendo `status`, `article_slug` e `article_title` inalterados.
        """
        update_data = {"prompt": "Partially updated prompt"}
        serializer = ImageArticleSerializer(instance=self.image_article, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_image_article = serializer.save()

        # O campo `prompt` deve ser atualizado, mas `status`, `article_slug` e `article_title` devem permanecer inalterados.
        self.assertEqual(updated_image_article.prompt, update_data["prompt"])
        self.assertEqual(updated_image_article.status, self.image_article.status)
        self.assertEqual(updated_image_article.article_slug, self.image_article.article_slug)
