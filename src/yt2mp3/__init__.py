"""
YouTube to MP3 Converter

A simple, interactive Python program to download YouTube videos and convert them to MP3 format.
"""

__version__ = "1.0.0"
__author__ = "yt2mp3"

from .config import ConfigManager
from .downloader import YouTubeDownloader
from .cli import CLI

__all__ = ["ConfigManager", "YouTubeDownloader", "CLI"]