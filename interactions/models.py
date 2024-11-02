# interactions/models.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

class InteractionType(models.TextChoices):
    FOLLOW = 'follow', _('Follow')
    LIKE = 'like', _('Like')

class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="initiated_interactions")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    interaction_type = models.CharField(max_length=50, choices=InteractionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id', 'interaction_type')

    def __str__(self):
        return f"{self.user.username} {self.interaction_type} {self.content_object}"
