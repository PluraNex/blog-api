import logging
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from articles.models import Article, ArticleTheme, Category, Tag
from userprofile.models import UserProfile
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class ArticleViewsTest(APITestCase):

    def setUp(self):
        # Configuração inicial para cada teste
        self.clear_previous_data()
        self.create_test_user()
        self.create_common_objects()
        self.create_additional_articles()

    def clear_previous_data(self):
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        Category.objects.all().delete()
        Article.objects.all().delete()

    def create_test_user(self):
        # Criação do usuário e do perfil conforme especificado
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.user_profile, _ = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={'is_author': True}
        )

    def create_common_objects(self):
        self.theme = ArticleTheme.objects.create(name="Technology")
        self.tag = Tag.objects.create(name="Tech")
        self.category = Category.objects.create(name="Software")
        self.article = Article.objects.create(
            title="Test Article",
            content="Sample content",
            author=self.user_profile,
            theme=self.theme,
            visibility="published",
            views_count=10,
            reading_time_minutes=5
        )
        self.article.tags.add(self.tag)
        self.article.categories.add(self.category)

    def create_additional_articles(self):
        for i in range(1, 4):
            article = Article.objects.create(
                title=f"Additional Article {i}",
                content="Additional content",
                author=self.user_profile,
                theme=self.theme,
                visibility="published",
                views_count=10 * i,
                reading_time_minutes=5
            )
            article.tags.add(self.tag)
            article.categories.add(self.category)

    def test_article_list_view(self):
        url = reverse("article-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_article_detail_view_by_id(self):
        url = reverse("article-detail", args=[self.article.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.article.title)

    def test_article_theme_list_view(self):
        url = reverse("article-themes-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_article_create_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("article-create")
        data = {
            "title": "New Article",
            "content": "Content for new article",
            "author": self.user.username,  # Utilize o username em vez do ID
            "theme": self.theme.name,  # Nome do tema conforme o serializer espera
            "visibility": "draft"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_article_search_view(self):
        url = reverse("article-search") + "?keywords=Test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_trending_articles_view(self):
        url = reverse("trending-articles") + "?limit=5"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filtered_sorted_article_view(self):
        url = reverse("filtered-sorted-articles") + "?sort_by=views_count&order=desc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_articles_by_author_view(self):
        url = reverse("articles-by-author", args=[self.user_profile.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_article_tag_update_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("article-tags-update", args=[self.article.id])
        data = {"tags": ["Updated Tag"]}
        response = self.client.put(url, data, format="json")  # Adicione o formato JSON
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_statistics_view(self):
        url = reverse("article-statistics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_views", response.data)

    def test_article_update_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("article-update", args=[self.article.id])
        data = {
            "title": "Updated Article Title",
            "content": "Updated content",
            "author": self.user.username  # Utilize o username em vez do ID
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Article Title")

    def test_articles_by_author_view_invalid_page(self):
        url = reverse("articles-by-author", args=[self.user_profile.id]) + "?page=invalid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_articles_by_author_view_empty_page(self):
        url = reverse("articles-by-author", args=[self.user_profile.id]) + "?page=9999"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_article_detail_view_by_slug(self):
        url = reverse("article-detail-slug", args=[self.article.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.article.title)

    def test_article_detail_view_not_found(self):
        url = reverse("article-detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Article not found"})

    def test_trending_articles_view_invalid_limit(self):
        url = reverse("trending-articles") + "?limit=invalid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_trending_articles_view_unexpected_error(self):
        with patch("articles.models.Article.objects.order_by", side_effect=Exception("Test error")):
            url = reverse("trending-articles") + "?limit=5"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("error", response.data)

    def test_filtered_sorted_article_view_invalid_sort(self):
            url = reverse("filtered-sorted-articles") + "?sort_by=invalid_field&order=desc"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_filtered_sorted_article_view_invalid_order(self):
            url = reverse("filtered-sorted-articles") + "?sort_by=views_count&order=invalid_order"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_articles_by_author_view_author_not_found(self):
            url = reverse("articles-by-author", args=[9999])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data, {"error": "Author not found"})

    def test_article_tag_update_view_invalid_data(self):
            self.client.force_authenticate(user=self.user)
            url = reverse("article-tags-update", args=[self.article.id])
            data = {"tags": "invalid_format"}
            response = self.client.put(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_article_tag_update_view_article_not_found(self):
            self.client.force_authenticate(user=self.user)
            url = reverse("article-tags-update", args=[9999])
            data = {"tags": ["Updated Tag"]}
            response = self.client.put(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data, {"error": "Article not found"})

    def test_article_update_view_article_not_found(self):
            self.client.force_authenticate(user=self.user)
            url = reverse("article-update", args=[9999])
            data = {"title": "Updated Title"}
            response = self.client.put(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data, {"error": "Article not found"})