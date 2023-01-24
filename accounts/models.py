from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', null=True, blank=True)
    email = models.EmailField(db_index=True, unique=True, max_length=254)

    def clean(self):
        self.email = self.email.lower()
        return super().clean()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
