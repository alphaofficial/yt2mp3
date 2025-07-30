import os
import yt_dlp
from typing import Dict, Any, Optional
from .config import ConfigManager


class YouTubeDownloader:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
    
    def validate_url(self, url: str) -> bool:
        return "youtube.com" in url or "youtu.be" in url
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown')
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def download(self, url: str) -> bool:
        if not self.validate_url(url):
            print("Error: Invalid YouTube URL")
            return False
        
        download_path = self.config.get_download_path()
        
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except OSError as e:
                print(f"Error creating download directory: {e}")
                return False
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]',
            'outtmpl': os.path.join(download_path, self.config.config["filename_format"]),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.config.config["audio_quality"],
            }],
            'extractaudio': True,
            'audioformat': 'mp3',
            'keepvideo': self.config.config.get("keep_video", False),
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading to: {download_path}")
                ydl.download([url])
                print("Download completed successfully!")
                return True
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False