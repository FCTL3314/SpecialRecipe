from django.urls import path

from interactions.views import AddCommentCreateView, BookmarksListView

app_name = 'interactions'

urlpatterns = [
    path('bookmarks/', BookmarksListView.as_view(), name='bookmarks'),
    path('comment/add/<int:recipe_id>/', AddCommentCreateView.as_view(), name='comment-add'),
]
