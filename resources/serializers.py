# resources/serializers.py
from rest_framework import serializers
from .models import ImageArticle

class ImageArticleSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source="image", read_only=True)
    article_title = serializers.ReadOnlyField(source="article.title") 

    class Meta:
        model = ImageArticle
        fields = [
            "id",
            "prompt",
            "image_url",
            "article",
            "article_slug",
            "created_at",
            "updated_at",
            "status",
            "article_title",
        ]
        read_only_fields = [
            "article_slug",
            "created_at",
            "updated_at",
        ]