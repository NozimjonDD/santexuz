from django.urls import path, include

urlpatterns = [
    path("auth/", include("apps.api.v1.auth.urls")),
    path("admin/", include("apps.api.v1.admin.urls")),
    path("site/", include("apps.api.v1.site.urls")),
    path("testing/", include("apps.api.v1.testing.urls")),
]
