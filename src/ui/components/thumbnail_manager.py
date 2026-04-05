import os
import subprocess
from pathlib import Path


class ThumbnailManager:
    """Manages video thumbnail generation and caching"""

    CACHE_DIR = Path.home() / ".cache" / "snow-engine" / "thumbnails"
    VIDEO_EXTENSIONS = (".mp4", ".webm", ".mkv", ".avi", ".mov", ".gif")

    @classmethod
    def get_cache_dir(cls):
        """Get or create thumbnail cache directory"""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CACHE_DIR

    @classmethod
    def get_thumbnail(cls, video_path):
        """Generate or retrieve cached thumbnail for a video

        Args:
            video_path: Path to the video file

        Returns:
            Path to thumbnail or None if generation failed
        """
        cache_dir = cls.get_cache_dir()
        thumb_name = os.path.basename(video_path).replace(" ", "_") + ".jpg"
        thumb_path = cache_dir / thumb_name

        if not thumb_path.exists():
            success = cls._generate_thumbnail(video_path, thumb_path)
            if not success:
                return None

        return str(thumb_path) if thumb_path.exists() else None

    @classmethod
    def _generate_thumbnail(cls, video_path, output_path):
        """Generate thumbnail using ffmpeg

        Args:
            video_path: Path to the video file
            output_path: Where to save the thumbnail

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    video_path,
                    "-ss",
                    "00:00:01",
                    "-vframes",
                    "1",
                    "-vf",
                    "scale=320:180:force_original_aspect_ratio=increase,crop=320:180",
                    "-q:v",
                    "2",
                    str(output_path),
                ],
                capture_output=True,
                timeout=10,
            )
            return True
        except Exception:
            return False

    @classmethod
    def get_youtube_thumbnail_path(cls, video_id):
        """Get path to cached YouTube thumbnail

        Args:
            video_id: YouTube video ID

        Returns:
            Path to cached thumbnail or None
        """
        cache_dir = cls.get_cache_dir()
        thumb_path = cache_dir / f"yt_{video_id}.jpg"
        return (
            str(thumb_path)
            if thumb_path.exists() and thumb_path.stat().st_size > 1000
            else None
        )

    @classmethod
    def save_youtube_thumbnail(cls, video_id, url):
        """Download and save YouTube thumbnail

        Args:
            video_id: YouTube video ID
            url: YouTube thumbnail URL

        Returns:
            True if successful, False otherwise
        """
        cache_dir = cls.get_cache_dir()
        thumb_path = cache_dir / f"yt_{video_id}.jpg"

        try:
            subprocess.run(
                ["curl", "-s", "-o", str(thumb_path), "-L", url],
                capture_output=True,
                timeout=10,
            )
            return thumb_path.exists() and thumb_path.stat().st_size > 1000
        except Exception:
            return False
