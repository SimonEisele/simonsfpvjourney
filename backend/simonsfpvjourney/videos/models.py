import uuid
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from videos.services.youtube import fetch_video_stats


# ----------------------------------------------------------------------------------------------------
# General Models
# ----------------------------------------------------------------------------------------------------
class TimeOfDay(models.TextChoices):
    MORNING = 'Morning', _('Morning')
    AFTERNOON = 'Afternoon', _('Afternoon')
    EVENING = 'Evening', _('Evening')
    NIGHT = 'Night', _('Night')
    SUNRISE = 'Sunrise', _('Sunrise')
    GOLDEN_HOUR = 'Golden Hour', _('Golden Hour')
    SUNSET = 'Sunset', _('Sunset')


class Season(models.TextChoices):
    SPRING = 'Spring', _('Spring')
    SUMMER = 'Summer', _('Summer')
    AUTUMN = 'Autumn', _('Autumn')
    WINTER = 'Winter', _('Winter')


class Weather(models.TextChoices):
    SUNNY = 'Sunny', _('Sunny')
    CLOUDY = 'Cloudy', _('Cloudy')
    RAINY = 'Rainy', _('Rainy')
    SNOWY = 'Snowy', _('Snowy')
    FOGGY = 'Foggy', _('Foggy')


# ----------------------------------------------------------------------------------------------------
# Drone Model
# ----------------------------------------------------------------------------------------------------
class Drone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='drones/')

    size_inch = models.FloatField()
    weight_grams = models.PositiveIntegerField()

    frame = models.CharField(max_length=100, blank=True)
    motors = models.CharField(max_length=100, blank=True)
    esc = models.CharField(max_length=100, blank=True)
    flight_controller = models.CharField(max_length=100, blank=True)
    camera = models.CharField(max_length=100, blank=True)
    vtx = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ----------------------------------------------------------------------------------------------------
# Category Model
# ----------------------------------------------------------------------------------------------------
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ----------------------------------------------------------------------------------------------------
# Tags Model
# ----------------------------------------------------------------------------------------------------
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# ----------------------------------------------------------------------------------------------------
# Video Model
# ----------------------------------------------------------------------------------------------------
class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # General video data
    title = models.CharField(max_length=200)
    youtube_id = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')

    # Information
    drone = models.ForeignKey(Drone, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    category = models.ForeignKey(Category, related_name='videos', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    season = models.CharField(max_length=20, choices=Season.choices, blank=True)
    time_of_day = models.CharField(max_length=20, choices=TimeOfDay.choices, blank=True)
    weather = models.CharField(max_length=20, choices=Weather.choices, blank=True)

    # Youtube stats
    likes_current = models.PositiveIntegerField(default=0)
    views_current = models.PositiveIntegerField(default=0)
    comments_current = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)

    # Location
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    place = models.CharField(max_length=100, blank=True)

    # Dates
    date_recorded = models.DateField(db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # Visibility
    is_published = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['category', 'country', 'date_recorded']),

            models.Index(fields=['country', 'state']),

            models.Index(fields=['date_recorded']),

            models.Index(fields=['-views_current']),
            models.Index(fields=['-likes_current']),
        ]

    def update_stats(self):
        data = fetch_video_stats(self.youtube_id)
        if not data:
            return

        VideoStats.objects.create(
            video=self,
            likes=data["likes"],
            views=data["views"],
            comments=data["comments"],
            duration=data["duration"],
            fetched_at=now(),
        )

        self.likes_current = data["likes"]
        self.views_current = data["views"]
        self.comments_current = data["comments"]
        self.duration = data["duration"]
        self.save(update_fields=[
            'likes_current',
            'views_current',
            'comments_current',
            'duration'
        ])

    def __str__(self):
        return self.title


# ----------------------------------------------------------------------------------------------------
# Historical Stats Model
# ----------------------------------------------------------------------------------------------------
class VideoStats(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='stats')
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fetched_at']

    def __str__(self):
        return f"Stats for {self.video.title} at {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"


# ----------------------------------------------------------------------------------------------------
# Picture Model
# ----------------------------------------------------------------------------------------------------
class Picture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='pictures')
    image = models.ImageField(upload_to='pictures/')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Picture for {self.video.title}"


# ----------------------------------------------------------------------------------------------------
# Feedback Model
# ----------------------------------------------------------------------------------------------------
class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Submitted content
    message = models.TextField()
    category = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=200, blank=True)

    # Optional context
    page_url = models.URLField(blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    # Moderation
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback {self.id} ({self.category or 'general'})"
