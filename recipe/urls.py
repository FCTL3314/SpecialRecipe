from django.contrib.auth.decorators import login_required
from django.urls import path

from recipe.views import (DescriptionView, RecipesListView, SavesListView,
                          add_to_saved, remove_from_saved)

app_name = 'recipe'

urlpatterns = [
    path('description/<slug:recipe_slug>/', DescriptionView.as_view(), name='description'),
    path('category/<slug:category_slug>/', RecipesListView.as_view(), name='category'),
    path('page/<int:page>/', RecipesListView.as_view(), name='paginator'),
    path('category/<slug:category_slug>/page/<int:page>/', RecipesListView.as_view(), name='category_paginator'),
    path('saves/add/<int:recipe_id>/', add_to_saved, name='add_to_saved'),
    path('saves/remove/<int:recipe_id>/', remove_from_saved, name='remove_from_saved'),
    path('saves/', login_required(SavesListView.as_view()), name='saves'),
]
