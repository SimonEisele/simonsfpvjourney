from rest_framework.routers import DefaultRouter  # type: ignore
from django.urls import path
from .views import (
    DroneViewSet,
    VideoViewSet,
    CategoryViewSet,
    TagViewSet,
    PictureViewSet,
    FeedbackViewSet,
    trigger_fetch_video_stats,
)

router = DefaultRouter()
router.register(r'videos', VideoViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'drones', DroneViewSet)
router.register(r'pictures', PictureViewSet)
router.register(r'feedback', FeedbackViewSet)

urlpatterns = router.urls
urlpatterns.insert(
    0,
    path('ops/fetch-video-stats/', trigger_fetch_video_stats, name='ops-fetch-video-stats'),
)
# End of URL patterns.
