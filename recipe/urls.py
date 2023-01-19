from django.urls import path

from recipe.views import RecipesListView, DescriptionView, add_to_saved, remove_from_saved


app_name = 'recipe'

urlpatterns = [
    path('', RecipesListView.as_view(), name='recipes'),
    path('description/<int:recipe_id>/', DescriptionView.as_view(), name='description'),
    path('category/<int:category_id>/', RecipesListView.as_view(), name='category'),
    path('page/<int:page>/', RecipesListView.as_view(), name='paginator'),
    path('category/<int:category_id>/page/<int:page>/', RecipesListView.as_view(), name='category_paginator'),
    path('saves/add/<int:recipe_id>/', add_to_saved, name='add_to_saved'),
    path('saves/remove/<int:recipe_id>/', remove_from_saved, name='remove_from_saved'),
]
