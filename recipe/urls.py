from django.contrib.auth.decorators import login_required
from django.urls import path

from recipe.views import (BookmarksListView, DescriptionView, RecipesListView,
                          add_to_bookmarks, remove_from_bookmarks)

app_name = 'recipe'

urlpatterns = [
    path('description/<slug:recipe_slug>/', DescriptionView.as_view(), name='description'),
    path('category/<slug:category_slug>/', RecipesListView.as_view(), name='category'),
    path('page/<int:page>/', RecipesListView.as_view(), name='paginator'),
    path('category/<slug:category_slug>/page/<int:page>/', RecipesListView.as_view(), name='category-paginator'),
    path('saves/add/<int:recipe_id>/', add_to_bookmarks, name='add-to-bookmarks'),
    path('saves/remove/<int:recipe_id>/', remove_from_bookmarks, name='remove-from-bookmarks'),
    path('saves/', login_required(BookmarksListView.as_view()), name='bookmarks'),
]
