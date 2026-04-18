from django.contrib import admin
from django.utils.html import format_html
from .models import Drone, Video, Category, Tag, VideoStats, Picture, Feedback


class VideoStatsInline(admin.TabularInline):
    model = VideoStats
    extra = 0
    readonly_fields = ('likes', 'views', 'comments', 'duration', 'fetched_at')
    ordering = ('-fetched_at',)
    can_delete = False


class PictureInline(admin.StackedInline):
    model = Picture
    extra = 0
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)
    can_delete = True

    def image_preview(self, obj):
        image = getattr(obj, 'image', None)
        if not image:
            return '(no image)'
        try:
            url = image.url
        except Exception:
            url = str(image)
        if not url:
            return '(no image)'
        return format_html('<img src="{}" style="height:80px;border-radius:4px;" />', url)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'video_count')
    search_fields = ('name',)
    ordering = ('name',)

    def video_count(self, obj):
        return obj.videos.count()

    video_count.short_description = 'Videos'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'video_count')
    search_fields = ('name',)
    ordering = ('name',)

    def video_count(self, obj):
        return obj.video_set.count()

    video_count.short_description = 'Videos'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail_preview',
        'title',
        'category',
        'drone',
        'views_current',
        'likes_current',
        'comments_current',
        'date_recorded',
        'is_published',
    )

    list_filter = (
        'category',
        'drone',
        'season',
        'time_of_day',
        'weather',
        'is_published',
        'date_recorded',
    )

    search_fields = (
        'title',
        'description',
        'youtube_id',
        'tags__name',
    )

    autocomplete_fields = ('category', 'tags', 'drone')
    filter_horizontal = ('tags',)

    readonly_fields = (
        'thumbnail_preview',
        'likes_current',
        'views_current',
        'comments_current',
        'date_added',
        'date_updated',
    )

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'youtube_id', 'description', 'thumbnail', 'thumbnail_preview')
        }),
        ('Classification', {
            'fields': ('category', 'tags', 'drone')
        }),
        ('Environment', {
            'fields': ('season', 'time_of_day', 'weather')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'altitude', 'country', 'state', 'place')
        }),
        ('Stats (current)', {
            'fields': ('views_current', 'likes_current', 'comments_current', 'duration')
        }),
        ('Visibility & Dates', {
            'fields': ('is_published', 'date_recorded', 'date_added', 'date_updated')
        }),
    )

    inlines = [VideoStatsInline, PictureInline]

    ordering = ('-date_recorded',)

    # Allow quick toggle of publication status from the list view
    list_editable = ('is_published',)

    def thumbnail_preview(self, obj):
        thumbnail = getattr(obj, 'thumbnail', None)
        if not thumbnail:
            return '(no image)'
        try:
            url = thumbnail.url  # Image/FileField
        except Exception:
            url = str(thumbnail)  # URL/CharField
        if not url:
            return '(no image)'
        return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', url)

    thumbnail_preview.short_description = 'Thumbnail'


@admin.register(VideoStats)
class VideoStatsAdmin(admin.ModelAdmin):
    list_display = ('video', 'views', 'likes', 'comments', 'fetched_at')
    list_filter = ('fetched_at',)
    search_fields = ('video__title',)
    ordering = ('-fetched_at',)


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('image_thumb', 'video')
    list_filter = ('video',)
    search_fields = ('video__title',)
    ordering = ('-id',)
    readonly_fields = ('image_thumb',)

    def image_thumb(self, obj):
        image = getattr(obj, 'image', None)
        if not image:
            return '(no image)'
        try:
            url = image.url
        except Exception:
            url = str(image)
        if not url:
            return '(no image)'
        return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', url)

    image_thumb.short_description = 'Image'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'size_inch',
        'weight_grams',
        'camera',
        'is_active',
        'video_count',
    )

    list_filter = (
        'is_active',
        'size_inch',
    )

    search_fields = (
        'name',
        'frame',
        'motors',
        'esc',
        'flight_controller',
        'camera',
        'vtx',
    )

    ordering = ('name',)

    list_editable = ('is_active',)

    fieldsets = (
        ('General', {
            'fields': ('name', 'is_active', 'image')
        }),
        ('Specs', {
            'fields': ('size_inch', 'weight_grams')
        }),
        ('Components', {
            'fields': (
                'frame',
                'motors',
                'esc',
                'flight_controller',
                'camera',
                'vtx',
            )
        }),
    )

    def video_count(self, obj):
        return obj.videos.count()

    video_count.short_description = 'Videos'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'category', 'name', 'contact', 'is_reviewed')
    list_filter = ('is_reviewed', 'category', 'created_at')
    search_fields = ('message', 'name', 'contact', 'page_url')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
