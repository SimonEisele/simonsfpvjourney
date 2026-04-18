from rest_framework import serializers  # type: ignore
from .models import Category, Tag, VideoStats, Video, Drone, Picture, Feedback


# ----------------------------------------------------------------------------------------------------
# Category Serializer
# ----------------------------------------------------------------------------------------------------
class CategorySerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'video_count']


# ----------------------------------------------------------------------------------------------------
# Tag Serializer
# ----------------------------------------------------------------------------------------------------
class TagSerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'video_count']


# ----------------------------------------------------------------------------------------------------
# Drone Serializer
# ----------------------------------------------------------------------------------------------------
class DroneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = ['id', 'name', 'image', 'size_inch', 'weight_grams', 'frame', 'motors', 'esc',
                  'flight_controller', 'camera', 'vtx']


# ----------------------------------------------------------------------------------------------------
# VideoStats Serializer
# ----------------------------------------------------------------------------------------------------
class VideoStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoStats
        fields = ['likes', 'views', 'comments', 'duration', 'fetched_at']
        read_only_fields = ['likes', 'views', 'comments', 'duration', 'fetched_at']


# ----------------------------------------------------------------------------------------------------
# Video Serializer
# ----------------------------------------------------------------------------------------------------
class VideoSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    drone = DroneSerializer(read_only=True)
    stats = VideoStatsSerializer(many=True, read_only=True)
    pictures_count = serializers.IntegerField(read_only=True)

    # Lightweight nested pictures for faster single-fetch loading
    class VideoPictureSerializer(serializers.ModelSerializer):
        class Meta:
            model = Picture
            fields = ['id', 'image', 'created_at']

    pictures = VideoPictureSerializer(many=True, read_only=True)

    # Optional: übersetzbare Felder explizit markieren (falls nötig)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'youtube_id', 'description', 'thumbnail',
            'category', 'tags', 'drone',
            'likes_current', 'views_current', 'comments_current', 'duration',
            'latitude', 'longitude', 'altitude', 'country', 'state', 'place',
            'season', 'time_of_day', 'weather',
            'date_added', 'date_updated', 'date_recorded',
            'is_published', 'pictures_count',
            'stats', 'pictures',
        ]


# ----------------------------------------------------------------------------------------------------
# Picture Serializer
# ----------------------------------------------------------------------------------------------------
class PictureSerializer(serializers.ModelSerializer):
    # Include minimal video info for map link
    video = serializers.PrimaryKeyRelatedField(read_only=True)
    video_latitude = serializers.FloatField(source='video.latitude', read_only=True)
    video_longitude = serializers.FloatField(source='video.longitude', read_only=True)
    video_title = serializers.CharField(source='video.title', read_only=True)
    video_place = serializers.CharField(source='video.place', read_only=True)

    class Meta:
        model = Picture
        fields = [
            'id', 'image', 'altitude', 'latitude', 'longitude',
            'video', 'video_title', 'video_latitude', 'video_longitude', 'video_place', 'created_at'
        ]


# ----------------------------------------------------------------------------------------------------
# Feedback Serializer
# ----------------------------------------------------------------------------------------------------
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id', 'created_at', 'updated_at',
            'message', 'category', 'name', 'contact',
            'page_url', 'user_agent', 'is_reviewed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_reviewed']
