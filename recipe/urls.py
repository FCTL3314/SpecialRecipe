from django.urls import path

from recipe.views import RecipeDetailView, RecipesListView

app_name = 'recipe'

urlpatterns = [
    path('', RecipesListView.as_view(), name='index'),
    path('detail/<slug:recipe_slug>/', RecipeDetailView.as_view(), name='detail'),
    path('category/<slug:category_slug>/', RecipesListView.as_view(), name='category'),
]
