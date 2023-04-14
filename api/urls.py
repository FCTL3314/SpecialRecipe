from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('', include('api.recipe.urls', namespace='recipe')),
    path('', include('api.accounts.urls', namespace='accounts'))
]
