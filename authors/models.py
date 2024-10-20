# authors/models.py
from django.db import models

class Author(models.Model):
    """Modelo para autores de artigos, incluindo biografia e imagem opcional."""

    name = models.CharField(max_length=100)
    biography = models.TextField(blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="author_images/", blank=True, null=True)

    class Meta:
        db_table = "authors"
        indexes = [
            models.Index(fields=["name"], name="author_name_idx"),
        ]

    def __str__(self):
        return self.name
