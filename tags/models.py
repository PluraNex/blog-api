from django.db import models

class Tag(models.Model):
    """Modelo para tags que podem ser associadas a artigos."""

    name = models.CharField(max_length=100)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return self.name
