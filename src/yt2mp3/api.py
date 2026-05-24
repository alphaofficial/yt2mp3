from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from .config import ConfigManager


def normalize_resolution(value: Optional[Union[str, int]]) -> Optional[int]:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        height = value
    else:
        text = str(value).strip().lower()
        if text.endswith("p"):
            text = text[:-1]
        if not text.isdigit():
            raise ValueError(f"Invalid resolution: {value!r}")
        height = int(text)
    if height <= 0:
        raise ValueError("Resolution must be positive")
    return height


@dataclass(frozen=True)
class DownloadResult:
    success: bool
    url: str
    output_path: Optional[str] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class DownloadRequest:
    video_url: str
    config_manager: Optional[ConfigManager] = None
    max_height: Optional[int] = None
    quality: Optional[str] = None
    keep_original_video: Optional[bool] = None

    def resolution(self, value: Union[str, int]) -> "DownloadRequest":
        return DownloadRequest(
            self.video_url,
            self.config_manager,
            normalize_resolution(value),
            self.quality,
            self.keep_original_video,
        )

    def audio_quality(self, value: Union[str, int]) -> "DownloadRequest":
        return DownloadRequest(
            self.video_url,
            self.config_manager,
            self.max_height,
            str(value),
            self.keep_original_video,
        )

    def keep_video(self, value: bool = True) -> "DownloadRequest":
        return DownloadRequest(
            self.video_url,
            self.config_manager,
            self.max_height,
            self.quality,
            bool(value),
        )

    def write(self, output: Optional[Union[str, Path]] = None) -> DownloadResult:
        from .downloader import YouTubeDownloader

        config_manager = self.config_manager or ConfigManager()
        downloader = YouTubeDownloader(config_manager)
        try:
            success = downloader.download_request(self, output=output)
        except Exception as exc:  # defensive API boundary
            return DownloadResult(False, self.video_url, error=str(exc))

        output_path = downloader.resolve_output_path(output) if output is not None else None
        return DownloadResult(success, self.video_url, output_path=output_path)


def url(video_url: str, *, config_manager: Optional[ConfigManager] = None) -> DownloadRequest:
    return DownloadRequest(video_url=video_url, config_manager=config_manager)
