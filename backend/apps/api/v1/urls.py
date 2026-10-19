from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.api.v1.auth.urls")),
    path("site/", include("apps.api.v1.site.urls")),
    path("admin/", include("apps.api.v1.admin.urls")),
    path("common/", include("apps.api.common.urls")),
]
