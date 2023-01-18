from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from recipe.models import Category, Recipe, Ingredient


class RecipesListView(ListView):
    model = Recipe
    context_object_name = 'recipes'
    template_name = 'recipe/recipe.html'

    paginate_by = 3

    def get_queryset(self):
        products = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        if category_id:
            return products.filter(category_id=category_id).order_by('name')
        else:
            return products.all().order_by('name')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe - Recipes'
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.kwargs.get('category_id')
        return context


class DescriptionView(TemplateView):
    template_name = 'recipe/recipe_description.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        recipe = Recipe.objects.all().get(id=self.kwargs.get('recipe_id'))
        ingredients = Ingredient.objects.filter(recipe=recipe)
        context['recipe'] = recipe
        context['ingredients'] = ingredients
        context['title'] = f'Special Recipe - {recipe.name}'
        return context
