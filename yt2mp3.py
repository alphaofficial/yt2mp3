#!/usr/bin/env python3

import sys
from importlib import import_module
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent / "src" / "yt2mp3"
__path__ = [str(_PACKAGE_DIR)]
__package__ = "yt2mp3"
sys.modules.setdefault("yt2mp3", sys.modules[__name__])

__version__ = "1.0.0"

_api = import_module("yt2mp3.api")
_cli = import_module("yt2mp3.cli")
_config = import_module("yt2mp3.config")
_downloader = import_module("yt2mp3.downloader")

DownloadRequest = _api.DownloadRequest
DownloadResult = _api.DownloadResult
normalize_resolution = _api.normalize_resolution
url = _api.url
CLI = _cli.CLI
ConfigManager = _config.ConfigManager
YouTubeDownloader = _downloader.YouTubeDownloader

__all__ = [
    "CLI",
    "ConfigManager",
    "DownloadRequest",
    "DownloadResult",
    "YouTubeDownloader",
    "__version__",
    "normalize_resolution",
    "url",
    "main",
]


def main():
    try:
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
