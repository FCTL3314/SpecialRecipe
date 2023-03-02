from rest_framework import serializers

from recipe.models import Category, Ingredient, Recipe


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

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
    slug = serializers.SlugField(required=False)
    ingredients = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_ingredients(obj):
        return IngredientSerializer(Ingredient.objects.filter(recipe=obj), many=True).data

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'description', 'cooking_description', 'category', 'category_id', 'ingredients',
                  'slug', 'views',)
