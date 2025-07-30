import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        downloads_path = str(Path.home() / "Downloads")
        return {
            "download_path": downloads_path,
            "audio_quality": "192",
            "filename_format": "%(title)s.%(ext)s",
            "keep_video": False
        }
    
    def load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            config = self.get_default_config()
            self.save_config(config)
            return config
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Using default configuration...")
            return self.get_default_config()
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
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