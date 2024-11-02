# userprofile/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="")
    is_author = models.BooleanField(default=False)
    follow_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        if not self.profile_picture:
            self.profile_picture = 'profile_pics/default-neutral-avatar.png'
        super().save(*args, **kwargs)
