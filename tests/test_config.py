import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from src.yt2mp3.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_get_default_config(self):
        config_manager = ConfigManager(self.config_file)
        default_config = config_manager.get_default_config()
        
        self.assertIn("download_path", default_config)
        self.assertIn("audio_quality", default_config)
        self.assertIn("filename_format", default_config)
        self.assertIn("keep_video", default_config)
        self.assertEqual(default_config["audio_quality"], "192")
        self.assertEqual(default_config["filename_format"], "%(title)s.%(ext)s")
        self.assertEqual(default_config["keep_video"], False)
    
    def test_load_config_creates_default_when_file_not_exists(self):
        config_manager = ConfigManager(self.config_file)
        
        self.assertTrue(os.path.exists(self.config_file))
        self.assertEqual(config_manager.config["audio_quality"], "192")
        self.assertEqual(config_manager.config["keep_video"], False)
    
    def test_load_config_reads_existing_file(self):
        test_config = {
            "download_path": "/custom/path",
            "audio_quality": "320",
            "filename_format": "custom_%(title)s.%(ext)s",
            "keep_video": True
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        config_manager = ConfigManager(self.config_file)
        
        self.assertEqual(config_manager.config["download_path"], "/custom/path")
        self.assertEqual(config_manager.config["audio_quality"], "320")
        self.assertEqual(config_manager.config["filename_format"], "custom_%(title)s.%(ext)s")
        self.assertEqual(config_manager.config["keep_video"], True)
    
    def test_load_config_handles_invalid_json(self):
        with open(self.config_file, 'w') as f:
            f.write("invalid json content")
        
        with patch('builtins.print') as mock_print:
            config_manager = ConfigManager(self.config_file)
            
            mock_print.assert_any_call("Using default configuration...")
            self.assertEqual(config_manager.config["audio_quality"], "192")
    
    def test_save_config(self):
        config_manager = ConfigManager(self.config_file)
        new_config = {
            "download_path": "/new/path",
            "audio_quality": "256",
            "filename_format": "new_%(title)s.%(ext)s"
        }
        
        config_manager.save_config(new_config)
        
        with open(self.config_file, 'r') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config["download_path"], "/new/path")
        self.assertEqual(saved_config["audio_quality"], "256")
        self.assertEqual(config_manager.config, new_config)
    
    def test_update_setting(self):
        config_manager = ConfigManager(self.config_file)
        original_quality = config_manager.config["audio_quality"]
        
        config_manager.update_setting("audio_quality", "320")
        
        self.assertEqual(config_manager.config["audio_quality"], "320")
        self.assertNotEqual(config_manager.config["audio_quality"], original_quality)
        
        with open(self.config_file, 'r') as f:
            saved_config = json.load(f)
        self.assertEqual(saved_config["audio_quality"], "320")
    
    @patch('os.path.expanduser')
    def test_get_download_path(self, mock_expanduser):
        mock_expanduser.return_value = "/expanded/path"
        
        config_manager = ConfigManager(self.config_file)
        config_manager.config["download_path"] = "~/Downloads"
        
        result = config_manager.get_download_path()
        
        mock_expanduser.assert_called_once_with("~/Downloads")
        self.assertEqual(result, "/expanded/path")
    
    @patch('builtins.print')
    def test_show_config(self, mock_print):
        config_manager = ConfigManager(self.config_file)
        config_manager.config = {
            "download_path": "/test/path",
            "audio_quality": "192"
        }
        
        config_manager.show_config()
        
        mock_print.assert_any_call("Current configuration:")
        mock_print.assert_any_call("  download_path: /test/path")
        mock_print.assert_any_call("  audio_quality: 192")
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('builtins.print')
    def test_save_config_handles_io_error(self, mock_print, mock_file):
        config_manager = ConfigManager(self.config_file)
        
        config_manager.save_config({"test": "value"})
        
        mock_print.assert_called_with("Error saving config: Permission denied")


if __name__ == '__main__':
    unittest.main()