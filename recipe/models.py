from django.db import models
from django.db.models import Count

from accounts.models import User
from common.cache import get_cached_data_or_set_new


class CategoryManager(models.Manager):
    categories_cache_time = 60 * 60

    def get_cached_queryset(self):
        return get_cached_data_or_set_new('categories', self.all, self.categories_cache_time)


class Category(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class RecipeManager(models.Manager):
    recipes_cache_time = 60 * 60
    popular_recipes_cache_time = 3600 * 24

    def get_cached_queryset(self):
        return get_cached_data_or_set_new('recipes', self.all, self.recipes_cache_time)

    def get_cached_popular_recipes(self):
        return get_cached_data_or_set_new(
            'popular_recipes',
            lambda: self.annotate(bookmarks_count=Count('bookmarks')).order_by('-bookmarks_count'),
            self.popular_recipes_cache_time,
        )

    def get_user_bookmarked_recipes(self, user):
        return self.filter(bookmarks=user) if user.is_authenticated else None


class Recipe(models.Model):
    image = models.ImageField(upload_to='recipe_images')
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    cooking_description = models.TextField()
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True)
    bookmarks = models.ManyToManyField(User, blank=True, through='RecipeBookmark')
    views = models.PositiveBigIntegerField(default=0)

    objects = RecipeManager()

    def __str__(self):
        return self.name

    def get_ingredients(self):
        return Ingredient.objects.filter(recipe=self)

    def get_comments(self):
        return Comment.objects.filter(recipe=self).prefetch_related('author')

    def bookmarks_count(self):
        return self.bookmarks.count()


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class RecipeBookmarkManager(models.Manager):

    def get_user_bookmarks(self, user):
        return self.filter(user=user).prefetch_related('recipe__bookmarks', 'recipe')


class RecipeBookmark(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = RecipeBookmarkManager()

    def __str__(self):
        return f'{self.user.username} | {self.recipe.name}'


class Comment(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    author = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL)
    text = models.CharField(max_length=516)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
