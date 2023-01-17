from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
