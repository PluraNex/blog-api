from babel.dates import format_date
from django.urls import reverse
from django.utils import translation
from rest_framework import serializers

from resources.serializers import ImageArticleSerializer

from .models import Article, ArticleTheme, UserProfile, Category, Tag
from tags.serializers import TagSerializer
from categories.serializers import CategorySerializer

class ArticleThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleTheme
        fields = ["id", "name"]


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.user.username", allow_blank=True)
    theme = serializers.CharField(source="theme.name", allow_blank=True, required=False)
    tags = TagSerializer(many=True, read_only=False, required=False)
    categories = CategorySerializer(many=True, read_only=True)
    image_article = ImageArticleSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    read_time = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    formatted_publication_date = serializers.SerializerMethodField()
    previous_post = serializers.SerializerMethodField()
    next_post = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "description",
            "content",
            "author",
            "publication_date",
            "formatted_publication_date",
            "theme",
            "tags",
            "categories",
            "reading_time_minutes",
            "image_article",
            "visibility",
            "views_count",
            "version",
            "slug",
            "image_url",
            "read_time",
            "category",
            "previous_post",
            "next_post",
            "absolute_url",
        ]
    

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image_article and obj.image_article.image:
            return (
                request.build_absolute_uri(obj.image_article.image.url)
                if request
                else obj.image_article.image.url
            )
        return None

    def get_read_time(self, obj):
        return obj.reading_time_minutes

    def get_category(self, obj):
        if obj.categories.exists():
            return obj.categories.first().name
        return "Sem Categoria"

    def get_formatted_publication_date(self, obj):
        if obj.publication_date:
            with translation.override("pt-br"):
                return format_date(
                    obj.publication_date, format="d MMMM y", locale="pt_BR"
                )
        return None

    def get_previous_post(self, obj):
        previous_post = (
            Article.objects.filter(publication_date__lt=obj.publication_date)
            .order_by("-publication_date")
            .first()
        )
        if previous_post:
            return {
                "title": previous_post.title,
                "url": reverse("single_post", args=[previous_post.slug]),
            }
        return None

    def get_next_post(self, obj):
        next_post = (
            Article.objects.filter(publication_date__gt=obj.publication_date)
            .order_by("publication_date")
            .first()
        )
        if next_post:
            return {
                "title": next_post.title,
                "url": reverse("single_post", args=[next_post.slug]),
            }
        return None

    def get_absolute_url(self, obj):
        """Retorna a URL absoluta do post."""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        categories_data = validated_data.pop("categories", [])
        author_username = validated_data.pop("author", {}).get("user", {}).get("username")
        theme_name = validated_data.pop("theme", {}).get("name")

        if author_username:
            try:
                author_profile = UserProfile.objects.get(user__username=author_username)
                validated_data["author"] = author_profile
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError(
                    {"author": "UserProfile not found for the given username."}
                )

        if theme_name:
            theme, _ = ArticleTheme.objects.get_or_create(name=theme_name)
            validated_data["theme"] = theme

        article = Article.objects.create(**validated_data)

        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_data["name"])
            article.tags.add(tag)

        for category_data in categories_data:
            category, _ = Category.objects.get_or_create(name=category_data["name"])
            article.categories.add(category)

        return article

    def search(self, keywords=None, theme=None, category=None, author=None):
        articles = Article.objects.all()

        if keywords:
            articles = articles.filter(title__icontains=keywords)

        if theme:
            articles = articles.filter(theme__name=theme)

        if category:
            articles = articles.filter(categories__name=category)

        if author:
            articles = articles.filter(author__user__username=author)

        return articles
