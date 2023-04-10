from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipe.urls', namespace='recipe')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('api/v1/', include('api.urls', namespace='api')),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
