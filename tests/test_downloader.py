import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from src.yt2mp3.config import ConfigManager
from src.yt2mp3.downloader import YouTubeDownloader


class TestYouTubeDownloader(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.config_manager = ConfigManager(self.config_file)
        self.downloader = YouTubeDownloader(self.config_manager)
        
    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_validate_url_valid_youtube_com(self):
        valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertTrue(self.downloader.validate_url(valid_url))
    
    def test_validate_url_valid_youtu_be(self):
        valid_url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertTrue(self.downloader.validate_url(valid_url))
    
    def test_validate_url_invalid(self):
        invalid_urls = [
            "https://vimeo.com/123456",
            "https://example.com",
            "not_a_url",
            ""
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.downloader.validate_url(url))
    
    @patch('src.yt2mp3.downloader.yt_dlp.YoutubeDL')
    def test_get_video_info_success(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        mock_info = {
            'title': 'Test Video',
            'duration': 180,
            'uploader': 'Test Channel'
        }
        mock_ydl.extract_info.return_value = mock_info
        
        url = "https://youtube.com/watch?v=test"
        result = self.downloader.get_video_info(url)
        
        self.assertEqual(result['title'], 'Test Video')
        self.assertEqual(result['duration'], 180)
        self.assertEqual(result['uploader'], 'Test Channel')
        mock_ydl.extract_info.assert_called_once_with(url, download=False)
    
    @patch('src.yt2mp3.downloader.yt_dlp.YoutubeDL')
    def test_get_video_info_missing_fields(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        mock_info = {}  # Empty info
        mock_ydl.extract_info.return_value = mock_info
        
        url = "https://youtube.com/watch?v=test"
        result = self.downloader.get_video_info(url)
        
        self.assertEqual(result['title'], 'Unknown')
        self.assertEqual(result['duration'], 0)
        self.assertEqual(result['uploader'], 'Unknown')
    
    @patch('src.yt2mp3.downloader.yt_dlp.YoutubeDL')
    @patch('builtins.print')
    def test_get_video_info_exception(self, mock_print, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Network error")
        
        url = "https://youtube.com/watch?v=test"
        result = self.downloader.get_video_info(url)
        
        self.assertIsNone(result)
        mock_print.assert_called_with("Error getting video info: Network error")
    
    @patch('builtins.print')
    def test_download_invalid_url(self, mock_print):
        invalid_url = "https://example.com"
        result = self.downloader.download(invalid_url)
        
        self.assertFalse(result)
        mock_print.assert_called_with("Error: Invalid YouTube URL")
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('src.yt2mp3.downloader.yt_dlp.YoutubeDL')
    def test_download_creates_directory(self, mock_ydl_class, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        self.config_manager.config["download_path"] = "/test/path"
        
        url = "https://youtube.com/watch?v=test"
        self.downloader.download(url)
        
        mock_makedirs.assert_called_once()
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_download_directory_creation_fails(self, mock_print, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        mock_makedirs.side_effect = OSError("Permission denied")
        
        url = "https://youtube.com/watch?v=test"
        result = self.downloader.download(url)
        
        self.assertFalse(result)
        mock_print.assert_called_with("Error creating download directory: Permission denied")
    
    @patch('os.path.exists')
    @patch('src.yt2mp3.downloader.yt_dlp.YoutubeDL')
    @patch('builtins.print')
    def test_download_success(self, mock_print, mock_ydl_class, mock_exists):
        mock_exists.return_value = True
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        self.config_manager.config["download_path"] = "/test/path"
        self.config_manager.config["audio_quality"] = "192"
        self.config_manager.config["filename_format"] = "%(title)s.%(ext)s"
        
        url = "https://youtube.com/watch?v=test"
        result = self.downloader.download(url)
        
        self.assertTrue(result)
        mock_ydl.download.assert_called_once_with([url])
        mock_print.assert_any_call("Download completed successfully!")
    
    @patch('os.path.exists')
    @patch('src.yt2mp3.downloader.yt_dlp.YoutubeDL')
    @patch('builtins.print')
    def test_download_ydl_exception(self, mock_print, mock_ydl_class, mock_exists):
        mock_exists.return_value = True
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.download.side_effect = Exception("Download failed")
        
        url = "https://youtube.com/watch?v=test"
        result = self.downloader.download(url)
        
        self.assertFalse(result)
        mock_print.assert_called_with("Error downloading video: Download failed")
    
    @patch('os.path.exists')
    @patch('src.yt2mp3.downloader.yt_dlp.YoutubeDL')
    def test_download_uses_correct_options(self, mock_ydl_class, mock_exists):
        mock_exists.return_value = True
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        self.config_manager.config["download_path"] = "/test/path"
        self.config_manager.config["audio_quality"] = "320"
        self.config_manager.config["filename_format"] = "custom_%(title)s.%(ext)s"
        
        url = "https://youtube.com/watch?v=test"
        self.downloader.download(url)
        
        # Check that YoutubeDL was called with correct options
        call_args = mock_ydl_class.call_args[0][0]
        self.assertEqual(call_args['format'], 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]')
        self.assertIn('FFmpegExtractAudio', call_args['postprocessors'][0]['key'])
        self.assertEqual(call_args['postprocessors'][0]['preferredcodec'], 'mp3')
        self.assertEqual(call_args['postprocessors'][0]['preferredquality'], '320')


if __name__ == '__main__':
    unittest.main()