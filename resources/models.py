from django.db import models
from django.utils.html import mark_safe

from articles.models import Article


class ImageArticle(models.Model):
    prompt = models.TextField()
    image = models.ImageField(upload_to="article_images/", null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="images", null=True, blank=True)
    article_slug = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        default="em revisão",
        choices=[
            ("aprovado", "Aprovado"),
            ("não aprovado", "Não Aprovado"),
            ("em revisão", "Em Revisão"),
        ],
    )

    def save(self, *args, **kwargs):
        if not self.article_slug:
            self.article_slug = self.article.slug
        super().save(*args, **kwargs)

    def image_tag(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" style="max-width:200px; max-height:200px;" />'
            )
        return "Nenhuma imagem disponível"

    image_tag.short_description = "Image Preview"

    def __str__(self):
        return f"ImageArticle ({self.status}) for {self.article}"
