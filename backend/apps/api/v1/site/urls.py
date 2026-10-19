from rest_framework.routers import DefaultRouter

from apps.api.v1.site.views import OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="site-order")
urlpatterns = router.urls
