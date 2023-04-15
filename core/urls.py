from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),

    path('', include('recipe.urls', namespace='recipe')),
    path('interactions/', include('interactions.urls', namespace='interactions')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('api/v1/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
