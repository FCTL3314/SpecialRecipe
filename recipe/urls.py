from django.urls import path

from recipe.views import RecipesListView


app_name = 'recipe'

urlpatterns = [
    path('', RecipesListView.as_view(), name='recipes'),
    path('category/<int:category_id>/', RecipesListView.as_view(), name='category'),
    path('page/<int:page>/', RecipesListView.as_view(), name='paginator'),
    path('category/<int:category_id>/page/<int:page>/', RecipesListView.as_view(), name='category_paginator'),
]
