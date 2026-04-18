from rest_framework.routers import DefaultRouter  # type: ignore
from .views import DroneViewSet, VideoViewSet, CategoryViewSet, TagViewSet, PictureViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'videos', VideoViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'drones', DroneViewSet)
router.register(r'pictures', PictureViewSet)
router.register(r'feedback', FeedbackViewSet)

urlpatterns = router.urls
