from babel.dates import format_date
from django.utils import translation
from rest_framework import serializers

from resources.models import ImageArticle
from tags.serializers import TagSerializer
from categories.serializers import CategorySerializer
from .models import Article, ArticleTheme, UserProfile, Tag, Category

class ArticleThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleTheme
        fields = ["id", "name"]

class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.user.username", allow_blank=True)
    theme = serializers.CharField(source="theme.name", allow_blank=True, required=False)
    tags = TagSerializer(many=True, required=False)
    categories = CategorySerializer(many=True, required=False)
    image_url = serializers.SerializerMethodField()  # Mantém apenas a URL da imagem
    read_time = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    formatted_publication_date = serializers.SerializerMethodField()
    previous_post = serializers.SerializerMethodField()
    next_post = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id", "title", "description", "content", "author", "publication_date",
            "formatted_publication_date", "theme", "tags", "categories",
            "reading_time_minutes", "image_url", "visibility", "views_count",
            "version", "slug", "read_time", "category", "previous_post", "next_post",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image_article and obj.image_article.image:
            return request.build_absolute_uri(obj.image_article.image.url) if request else obj.image_article.image.url
        return None
    
    def get_read_time(self, obj):
        return obj.reading_time_minutes

    def get_category(self, obj):
        return obj.categories.first().name if obj.categories.exists() else "Sem Categoria"

    def get_formatted_publication_date(self, obj):
        if obj.publication_date:
            with translation.override("pt-br"):
                return format_date(obj.publication_date, format="d MMMM y", locale="pt_BR")
        return None

    def get_previous_post(self, obj):
        previous_post = (
            Article.objects.filter(publication_date__lt=obj.publication_date)
            .order_by("-publication_date")
            .first()
        )
        if previous_post:
            return {"title": previous_post.title, "slug": previous_post.slug}
        return None

    def get_next_post(self, obj):
        next_post = (
            Article.objects.filter(publication_date__gt=obj.publication_date)
            .order_by("publication_date")
            .first()
        )
        if next_post:
            return {"title": next_post.title, "slug": next_post.slug}
        return None

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        categories_data = validated_data.pop("categories", [])
        image_article_data = validated_data.pop("image_article", None)
        
        # Tratamento para `author`
        author_username = validated_data.pop("author", {}).get("user", {}).get("username")
        if author_username:
            try:
                author_profile = UserProfile.objects.get(user__username=author_username)
                validated_data["author"] = author_profile
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError({"author": "UserProfile not found for the given username."})

        # Tratamento para `theme`
        theme_name = validated_data.pop("theme", {}).get("name")
        if theme_name:
            theme, _ = ArticleTheme.objects.get_or_create(name=theme_name)
            validated_data["theme"] = theme

        # Criação do artigo principal
        article = Article.objects.create(**validated_data)

        # Adicionando `tags`
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_data["name"])
            article.tags.add(tag)

        # Adicionando `categories`
        for category_data in categories_data:
            category, _ = Category.objects.get_or_create(name=category_data["name"])
            article.categories.add(category)

        # Criação e associação do `ImageArticle`, se fornecido
        if image_article_data:
            ImageArticle.objects.create(article=article, **image_article_data)

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


    def update_author(self, instance, author_data):
        if author_data:
            author_username = author_data.get("user", {}).get("username")
            if author_username:
                try:
                    author_profile = UserProfile.objects.get(user__username=author_username)
                    instance.author = author_profile
                except UserProfile.DoesNotExist:
                    raise serializers.ValidationError({"author": "UserProfile not found for the given username."})

    def update_theme(self, instance, theme_data):
        if theme_data:
            theme_name = theme_data.get("name")
            if theme_name:
                theme, _ = ArticleTheme.objects.get_or_create(name=theme_name)
                instance.theme = theme

    def update_tags(self, instance, tags_data):
        if tags_data:
            instance.tags.clear()  # Limpa tags atuais
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_data["name"])
                instance.tags.add(tag)

    def update_categories(self, instance, categories_data):
        if categories_data:
            instance.categories.clear()  # Limpa categorias atuais
            for category_data in categories_data:
                category, _ = Category.objects.get_or_create(name=category_data["name"])
                instance.categories.add(category)

    def update(self, instance, validated_data):
        # Atualiza `author`, `theme`, `tags` e `categories` separadamente
        self.update_author(instance, validated_data.pop("author", None))
        self.update_theme(instance, validated_data.pop("theme", None))
        self.update_tags(instance, validated_data.pop("tags", []))
        self.update_categories(instance, validated_data.pop("categories", []))

        # Atualização dos demais campos diretamente no artigo
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance