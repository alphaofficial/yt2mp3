from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import yt_dlp

from .api import DownloadRequest, normalize_resolution
from .config import ConfigManager


class YouTubeDownloader:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def validate_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
        except (TypeError, ValueError):
            return False

        if parsed.scheme not in {"http", "https"}:
            return False

        host = (parsed.hostname or "").lower().rstrip(".")
        return host == "youtu.be" or host == "youtube.com" or host.endswith(".youtube.com")

    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            ydl_opts = {"quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", "Unknown"),
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None

    def resolve_output_path(self, output: Optional[Union[str, Path]]) -> str:
        download_path = Path(self.config.get_download_path()).expanduser().resolve()
        if output is None:
            return self.resolve_filename_template(download_path)
        output_path = Path(output).expanduser()
        if not output_path.is_absolute():
            output_path = download_path / output_path
        output_path = output_path.resolve()
        try:
            output_path.relative_to(download_path)
        except ValueError as exc:
            raise ValueError(f"Output path must stay within download directory: {download_path}") from exc
        return str(output_path)

    def resolve_filename_template(self, download_path: Optional[Path] = None) -> str:
        download_path = (download_path or Path(self.config.get_download_path())).expanduser().resolve()
        filename_format = self.config.config["filename_format"]
        template_path = Path(filename_format).expanduser()
        if template_path.is_absolute():
            candidate = template_path.resolve()
        else:
            candidate = (download_path / template_path).resolve()
        try:
            candidate.relative_to(download_path)
        except ValueError as exc:
            raise ValueError(f"filename_format must stay within download directory: {download_path}") from exc
        return str(candidate)

    def build_format_selector(self, max_height: Optional[int]) -> str:
        height = max_height or normalize_resolution(self.config.config.get("resolution")) or 480
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/bestaudio"

    def build_ydl_options(
        self,
        *,
        output: Optional[Union[str, Path]] = None,
        max_height: Optional[int] = None,
        audio_quality: Optional[str] = None,
        keep_video: Optional[bool] = None,
    ) -> Dict[str, Any]:
        resolved_output = self.resolve_output_path(output)
        output_path = Path(resolved_output)
        if output is not None:
            outtmpl = str(output_path.with_suffix(".%(ext)s"))
        else:
            outtmpl = resolved_output
        quality = audio_quality or self.config.config["audio_quality"]
        return {
            "format": self.build_format_selector(max_height),
            "outtmpl": outtmpl,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": str(quality),
                }
            ],
            "extractaudio": True,
            "audioformat": "mp3",
            "keepvideo": self.config.config.get("keep_video", False) if keep_video is None else keep_video,
        }

    def download_request(self, request: DownloadRequest, output: Optional[Union[str, Path]] = None) -> bool:
        return self.download(
            request.video_url,
            output=output,
            max_height=request.max_height,
            audio_quality=request.quality,
            keep_video=request.keep_original_video,
        )

    def download(
        self,
        url: str,
        *,
        output: Optional[Union[str, Path]] = None,
        max_height: Optional[int] = None,
        audio_quality: Optional[str] = None,
        keep_video: Optional[bool] = None,
    ) -> bool:
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

        ydl_opts = self.build_ydl_options(
            output=output,
            max_height=max_height,
            audio_quality=audio_quality,
            keep_video=keep_video,
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading to: {download_path}")
                ydl.download([url])
                print("Download completed successfully!")
                return True
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False
