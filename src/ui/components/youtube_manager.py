import re
from src.ui.components.thumbnail_manager import ThumbnailManager


class YouTubeManager:
    """Manages YouTube URL handling and thumbnail fetching"""

    YOUTUBE_PATTERNS = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})",
    ]

    THUMBNAIL_QUALITIES = [
        "maxresdefault.jpg",
        "hqdefault.jpg",
        "mqdefault.jpg",
    ]

    @staticmethod
    def extract_video_id(url):
        """Extract YouTube video ID from URL

        Args:
            url: YouTube URL

        Returns:
            Video ID or None if invalid
        """
        for pattern in YouTubeManager.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def get_thumbnail_urls(video_id):
        """Get list of thumbnail URLs for a video ID

        Args:
            video_id: YouTube video ID

        Returns:
            List of thumbnail URLs in order of preference
        """
        return [
            f"https://img.youtube.com/vi/{video_id}/{quality}"
            for quality in YouTubeManager.THUMBNAIL_QUALITIES
        ]

    @staticmethod
    def fetch_thumbnail(url, callback):
        """Fetch YouTube thumbnail in background thread

        Args:
            url: YouTube URL
            callback: Function to call with thumbnail path when done
        """
        video_id = YouTubeManager.extract_video_id(url)
        if not video_id:
            return

        # Check if already cached
        cached_path = ThumbnailManager.get_youtube_thumbnail_path(video_id)
        if cached_path:
            callback(cached_path)
            return

        # Download in background
        def download():
            for thumb_url in YouTubeManager.get_thumbnail_urls(video_id):
                if ThumbnailManager.save_youtube_thumbnail(video_id, thumb_url):
                    cached_path = ThumbnailManager.get_youtube_thumbnail_path(video_id)
                    if cached_path:
                        callback(cached_path)
                    return

        import threading

        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
