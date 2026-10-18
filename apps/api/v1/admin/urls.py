from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api.v1.admin import views

router = DefaultRouter()
router.register("regions", views.RegionViewSet, basename="admin-region")
router.register("service-groups", views.ServiceGroupViewSet, basename="admin-service-group")
router.register("services", views.ServiceViewSet, basename="admin-service")
router.register("service-rates", views.ServiceRateViewSet, basename="admin-service-rate")
router.register("materials", views.MaterialViewSet, basename="admin-material")
router.register("contract-templates", views.ContractTemplateViewSet, basename="admin-contract-template")
router.register("users", views.UserViewSet, basename="admin-user")
router.register("plumbers", views.PlumberProfileViewSet, basename="admin-plumber")
router.register("stores", views.StoreViewSet, basename="admin-store")
router.register("orders", views.OrderViewSet, basename="admin-order")
router.register("audit-events", views.AuditEventViewSet, basename="admin-audit-event")

urlpatterns = [
    path("service-center/", views.ServiceCenterView.as_view(), name="admin-service-center"),
    path("reports/", views.ReportView.as_view(), name="admin-reports"),
    path("", include(router.urls)),
]
