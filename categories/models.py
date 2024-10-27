#categories/models.py
from django.db import models

class Category(models.Model):
    """Modelo para categorias de artigos."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "categories"
        indexes = [
            models.Index(fields=["name"], name="category_name_idx"),
        ]

    def __str__(self):
        return self.name
