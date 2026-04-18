from django.core.management.base import BaseCommand
from videos.models import Video, VideoStats
from django.utils.timezone import now
from videos.services.youtube import fetch_video_stats_batch


class Command(BaseCommand):
    help = "Fetch YouTube statistics for all videos"

    def handle(self, *args, **options):
        videos = list(Video.objects.all())
        self.stdout.write(f"Updating stats for {len(videos)} videos...")
        # Batch by 50 (API limit)
        for i in range(0, len(videos), 50):
            chunk = videos[i:i+50]
            id_map = {v.youtube_id: v for v in chunk}
            stats_map = fetch_video_stats_batch(list(id_map.keys()))
            for yt_id, stats in stats_map.items():
                v = id_map.get(yt_id)
                if not v:
                    continue
                VideoStats.objects.create(
                    video=v,
                    likes=stats["likes"],
                    views=stats["views"],
                    comments=stats["comments"],
                    duration=stats["duration"],
                    fetched_at=now(),
                )
                v.likes_current = stats["likes"]
                v.views_current = stats["views"]
                v.comments_current = stats["comments"]
                v.duration = stats["duration"]
                v.save(update_fields=['likes_current', 'views_current', 'comments_current', 'duration'])
            self.stdout.write(f"Updated {len(stats_map)} videos in this batch.")
