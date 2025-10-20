from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, UserKeyManageSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r"keys", UserKeyManageSet, basename="authorizedkey")

urlpatterns = router.urls
