import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def get_yt2mp3_home() -> Path:
    default_home = Path(os.environ.get("HOME", "~")) / ".yt2mp3"
    return Path(os.environ.get("YT2MP3_HOME", default_home)).expanduser()


class ConfigManager:
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file).expanduser() if config_file else get_yt2mp3_home() / "config.json"
        self.config = self.load_config()

    def get_default_config(self) -> Dict[str, Any]:
        downloads_path = str(Path(os.environ.get("HOME", "~")) / "Downloads")
        return {
            "download_path": downloads_path,
            "audio_quality": "192",
            "filename_format": "%(title)s.%(ext)s",
            "keep_video": False,
            "resolution": "480",
        }

    def load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            config = self.get_default_config()
            self.save_config(config)
            return config

        try:
            with open(self.config_file, "r") as f:
                loaded = json.load(f)
            config = self.get_default_config()
            config.update(loaded)
            return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Using default configuration...")
            return self.get_default_config()

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config is None:
            config = self.config

        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            self.config = config
        except IOError as e:
            print(f"Error saving config: {e}")

    def update_setting(self, key: str, value: Any) -> None:
        self.config[key] = value
        self.save_config()

    def get_download_path(self) -> str:
        return os.path.expanduser(self.config["download_path"])

    def show_config(self) -> None:
        print("Current configuration:")
        for key, value in self.config.items():
            print(f"  {key}: {value}")
