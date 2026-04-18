from googleapiclient.discovery import build  # type: ignore
from django.conf import settings
from typing import Dict, List, Optional


def _parse_iso8601_duration(iso: str) -> int:
    """Convert ISO 8601 duration (e.g., 'PT3M21S') to seconds."""
    import re
    pattern = re.compile(r"P(?:(?P<days>\d+)D)?T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?")
    m = pattern.fullmatch(iso)
    if not m:
        return 0
    days = int(m.group('days') or 0)
    hours = int(m.group('hours') or 0)
    minutes = int(m.group('minutes') or 0)
    seconds = int(m.group('seconds') or 0)
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def fetch_video_stats(youtube_id: str) -> Optional[dict]:
    youtube = build(
        "youtube", "v3",
        developerKey=settings.YOUTUBE_API_KEY
    )

    response = youtube.videos().list(
        part="statistics,contentDetails",
        id=youtube_id
    ).execute()

    if not response.get("items"):
        return None

    item = response["items"][0]
    stats = item.get("statistics", {})
    details = item.get("contentDetails", {})

    return {
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "duration": _parse_iso8601_duration(details.get("duration", "PT0S")),
    }


def fetch_video_stats_batch(youtube_ids: List[str]) -> Dict[str, dict]:
    """Fetch stats for up to 50 YouTube IDs in one request.
    Returns a mapping youtube_id -> stats dict.
    """
    if not youtube_ids:
        return {}

    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
    response = youtube.videos().list(
        part="statistics,contentDetails",
        id=",".join(youtube_ids)
    ).execute()

    items = response.get("items", [])
    out: Dict[str, dict] = {}
    for item in items:
        vid = item.get("id")
        stats = item.get("statistics", {})
        details = item.get("contentDetails", {})
        out[vid] = {
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "duration": _parse_iso8601_duration(details.get("duration", "PT0S")),
        }
    return out
