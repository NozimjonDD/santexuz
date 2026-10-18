from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api.common import views

router = DefaultRouter()
router.register("regions", views.RegionViewSet, basename="region")
router.register("service-groups", views.ServiceGroupViewSet, basename="service-group")
router.register("services", views.ServiceViewSet, basename="service")
router.register("service-rates", views.ServiceRateViewSet, basename="service-rate")
router.register("materials", views.MaterialViewSet, basename="material")
router.register("plumbers", views.PlumberViewSet, basename="plumber")
router.register("stores", views.StoreViewSet, basename="store")

urlpatterns = [
    path("service-center/", views.ServiceCenterView.as_view(), name="service-center"),
    path("", include(router.urls)),
]
