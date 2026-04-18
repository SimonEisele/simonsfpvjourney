from rest_framework import viewsets, generics, filters  # type: ignore
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from django.db.models import Count
from django.utils import translation

from .models import Video, Category, Tag, Drone, Picture, Feedback
from .serializers import VideoSerializer, CategorySerializer, TagSerializer, DroneSerializer, PictureSerializer
from .serializers import FeedbackSerializer
from rest_framework.parsers import MultiPartParser, FormParser  # type: ignore
from rest_framework.decorators import action  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import status  # type: ignore


# ----------------------------------------------------------------------------------------------------
# Category ViewSet
# ----------------------------------------------------------------------------------------------------
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        lang = self.request.headers.get('Accept-Language', 'en')
        translation.activate(lang)

        return Category.objects.annotate(video_count=Count('videos')).filter(video_count__gt=0)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# ----------------------------------------------------------------------------------------------------
# Tag ViewSet
# ----------------------------------------------------------------------------------------------------
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        lang = self.request.headers.get('Accept-Language', 'en')
        translation.activate(lang)

        return Tag.objects.annotate(video_count=Count('video')).filter(video_count__gt=0)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# ----------------------------------------------------------------------------------------------------
# Drone ViewSet
# ----------------------------------------------------------------------------------------------------
class DroneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Drone.objects.filter(is_active=True)
    serializer_class = DroneSerializer


# ----------------------------------------------------------------------------------------------------
# Video ViewSet
# ----------------------------------------------------------------------------------------------------
class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'category__id': ['exact'],
        'tags__id': ['exact'],
        'drone__id': ['exact'],
        'season': ['exact'],
        'time_of_day': ['exact'],
        'weather': ['exact'],
        'date_recorded': ['gte', 'lte'],
        'is_published': ['exact'],
    }

    search_fields = ['title', 'description', 'tags__name', 'category__name', 'drone__name']
    ordering_fields = ['date_recorded', 'views_current', 'likes_current', 'comments_current']

    def get_queryset(self):
        lang = self.request.headers.get('Accept-Language')
        if lang:
            translation.activate(lang)

        qs = Video.objects.prefetch_related(
            'tags',
            'stats',
            'pictures',
        ).select_related(
            'category',
            'drone',
        ).annotate(pictures_count=Count('pictures')).all()

        # Optional: nur veröffentlichte Videos
        if self.action in ['list', 'retrieve']:
            qs = qs.filter(is_published=True)

        return qs

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser], url_path='pictures/bulk')
    def upload_pictures(self, request, pk=None):
        """Upload multiple images for a video via multipart form.
        Expect form fields: images (multiple), optional altitude, latitude, longitude per image not supported in bulk.
        """
        try:
            video = self.get_object()
        except Exception:
            return Response({'detail': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('images')
        if not files:
            return Response({'detail': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        for f in files:
            pic = Picture.objects.create(video=video, image=f)
            created.append(pic)

        serializer = PictureSerializer(created, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ----------------------------------------------------------------------------------------------------
# Video List API
# ----------------------------------------------------------------------------------------------------
class VideoListView(generics.ListAPIView):
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'category__id': ['exact'],
        'tags__id': ['exact'],
        'drone__id': ['exact'],
        'season': ['exact'],
        'time_of_day': ['exact'],
        'weather': ['exact'],
        'date_recorded': ['gte', 'lte'],
        'is_published': ['exact'],
    }

    search_fields = ['title', 'description', 'tags__name', 'category__name', 'drone__name']
    ordering_fields = ['date_recorded', 'views_current', 'likes_current', 'comments_current']

    def get_queryset(self):
        lang = self.request.headers.get('Accept-Language')
        if lang:
            translation.activate(lang)

        qs = Video.objects.prefetch_related(
            'tags',
            'stats',
            'pictures',
        ).select_related(
            'category',
            'drone',
        ).annotate(pictures_count=Count('pictures')).filter(is_published=True)
        return qs


# ----------------------------------------------------------------------------------------------------
# Picture ViewSet
# ----------------------------------------------------------------------------------------------------
class PictureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Picture.objects.select_related('video').all()
    serializer_class = PictureSerializer


# ----------------------------------------------------------------------------------------------------
# Feedback ViewSet
# ----------------------------------------------------------------------------------------------------
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        # Only staff can list/view feedback; public users see nothing here
        user = getattr(self.request, 'user', None)
        if user and user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # Attach basic context if available
        data.setdefault('user_agent', request.META.get('HTTP_USER_AGENT', '')[:255])
        data.setdefault('page_url', request.data.get('page_url', ''))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
