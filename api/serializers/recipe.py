from rest_framework import serializers

from api.serializers.accounts import UserSerializer
from recipe.models import Category, Comment, Ingredient, Recipe, RecipeBookmark


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(), source='recipe')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'recipe_id')


class RecipeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Category.objects.all(), source='category'
    )
    ingredients = serializers.SerializerMethodField(read_only=True)
    bookmarks_count = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_ingredients(obj):
        return IngredientSerializer(Ingredient.objects.filter(recipe=obj), many=True).data

    @staticmethod
    def get_bookmarks_count(obj):
        return obj.bookmarks.count()

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'description', 'cooking_description', 'category', 'category_id', 'ingredients',
                  'bookmarks_count', 'views')


class RecipeBookmarkSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = RecipeBookmark
        fields = ('id', 'recipe', 'user')


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    recipe = RecipeSerializer(read_only=True)
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'recipe', 'recipe_id', 'created_date')
