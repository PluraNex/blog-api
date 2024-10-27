# articles/models.py

from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify

from categories.models import Category
from tags.models import Tag
from userprofile.models import UserProfile

class ArticleTheme(models.Model):
    """Modelo para temas específicos de artigos."""
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "article_themes"

    def __str__(self):
        return self.name

class Article(models.Model):
    """Modelo para artigos, incluindo relações com autores, temas, tags e categorias"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = CKEditor5Field()
    author = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    publication_date = models.DateTimeField(auto_now_add=True)
    theme = models.ForeignKey("ArticleTheme", on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name="articles")
    categories = models.ManyToManyField(Category, related_name="articles")
    reading_time_minutes = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    image_article = models.ForeignKey("resources.ImageArticle", on_delete=models.SET_NULL, null=True, blank=True, related_name="images")
    visibility = models.CharField(max_length=10, choices=[("draft", "Rascunho"), ("published", "Publicado")], default="published")
    views_count = models.IntegerField(default=0)
    version = models.IntegerField(default=1)
    slug = models.SlugField(max_length=255, unique=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        db_table = "articles"
        indexes = [models.Index(fields=["title"], name="article_title_idx")]

    def __str__(self):
        return self.title
