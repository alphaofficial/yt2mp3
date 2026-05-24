"""
YouTube to MP3 Converter.

Composable API example:
    yt2mp3.url("https://youtube.com/watch?v=...").resolution("1080p").audio_quality("192").write("song.mp3")
"""

__version__ = "1.0.0"
__author__ = "yt2mp3"

from .api import DownloadRequest, DownloadResult, normalize_resolution, url
from .cli import CLI, main
from .config import ConfigManager
from .downloader import YouTubeDownloader

__all__ = [
    "ConfigManager",
    "DownloadRequest",
    "DownloadResult",
    "YouTubeDownloader",
    "CLI",
    "main",
    "normalize_resolution",
    "url",
]
