from django.db import models
from django.utils.text import slugify

from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    image = models.ImageField(upload_to='recipe_images')
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    cooking_description = models.TextField()
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True)
    saves = models.ManyToManyField(User, blank=True)
    views = models.PositiveBigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_ingredients(self):
        return Ingredient.objects.filter(recipe=self)

    def total_saves(self):
        return self.saves.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'


class Ingredient(models.Model):
    name = models.CharField(max_length=48)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
