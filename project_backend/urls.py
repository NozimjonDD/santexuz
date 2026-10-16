from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language

# from .swagger_conf import swagger_urlpatterns

# Non-i18n URL patterns
urlpatterns = [
    path('set-language/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    # path('ckeditor/', include('ckeditor_uploader.urls')),
]

# i18n URL patterns
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
)

urlpatterns += [
    path("api/", include('apps.api.urls')),
]

# urlpatterns += swagger_urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




