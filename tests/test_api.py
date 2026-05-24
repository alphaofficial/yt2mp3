import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src import yt2mp3
from src.yt2mp3.api import BatchDownloadRequest, DownloadRequest, normalize_resolution
from src.yt2mp3.config import ConfigManager


class TestComposableAPI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "config.json")
        self.config = ConfigManager(self.config_file)
        self.config.config["download_path"] = self.temp_dir

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)

    def test_package_root_exposes_fluent_url_builder(self):
        request = yt2mp3.url("https://youtube.com/watch?v=test")
        self.assertIsInstance(request, DownloadRequest)
        self.assertEqual(request.video_url, "https://youtube.com/watch?v=test")

    def test_package_root_exposes_fluent_urls_builder(self):
        request = yt2mp3.urls(["https://youtube.com/watch?v=one", "https://youtu.be/two"])
        self.assertIsInstance(request, BatchDownloadRequest)
        self.assertEqual(request.video_urls, ("https://youtube.com/watch?v=one", "https://youtu.be/two"))

    def test_resolution_normalization(self):
        self.assertEqual(normalize_resolution("1080p"), 1080)
        self.assertEqual(normalize_resolution("720"), 720)
        self.assertIsNone(normalize_resolution(None))
        with self.assertRaises(ValueError):
            normalize_resolution("abc")

    @patch("src.yt2mp3.downloader.yt_dlp.YoutubeDL")
    def test_fluent_write_passes_resolution_quality_and_output(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = (
            yt2mp3.url("https://youtube.com/watch?v=test", config_manager=self.config)
            .resolution("1080p")
            .audio_quality("320")
            .write("song.mp3")
        )

        self.assertTrue(result.success)
        self.assertEqual(result.url, "https://youtube.com/watch?v=test")
        self.assertEqual(result.output_path, str(Path(self.temp_dir, "song.mp3").resolve()))
        opts = mock_ydl_class.call_args[0][0]
        self.assertIn("height<=1080", opts["format"])
        self.assertEqual(opts["postprocessors"][0]["preferredquality"], "320")
        self.assertEqual(opts["outtmpl"], str(Path(self.temp_dir, "song.%(ext)s").resolve()))

    @patch("src.yt2mp3.downloader.yt_dlp.YoutubeDL")
    def test_request_write_defaults_to_config(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        self.config.config["audio_quality"] = "128"

        result = DownloadRequest("https://youtu.be/test", config_manager=self.config).write()

        self.assertTrue(result.success)
        opts = mock_ydl_class.call_args[0][0]
        self.assertIn("height<=480", opts["format"])
        self.assertEqual(opts["postprocessors"][0]["preferredquality"], "128")

    @patch("src.yt2mp3.downloader.yt_dlp.YoutubeDL")
    def test_batch_write_all_applies_shared_options_sequentially(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        results = (
            yt2mp3.urls(["https://youtube.com/watch?v=one", "https://youtu.be/two"], config_manager=self.config)
            .resolution("720p")
            .audio_quality("128")
            .keep_video(True)
            .write_all()
        )

        self.assertEqual([result.success for result in results], [True, True])
        self.assertEqual([result.url for result in results], ["https://youtube.com/watch?v=one", "https://youtu.be/two"])
        self.assertEqual(mock_ydl.download.call_args_list[0][0][0], ["https://youtube.com/watch?v=one"])
        self.assertEqual(mock_ydl.download.call_args_list[1][0][0], ["https://youtu.be/two"])
        opts = mock_ydl_class.call_args[0][0]
        self.assertIn("height<=720", opts["format"])
        self.assertEqual(opts["postprocessors"][0]["preferredquality"], "128")
        self.assertTrue(opts["keepvideo"])

    @patch("src.yt2mp3.downloader.yt_dlp.YoutubeDL")
    def test_batch_write_all_rejects_output_to_avoid_overwrite(self, mock_ydl_class):
        results = yt2mp3.urls(["https://youtube.com/watch?v=one", "https://youtu.be/two"], config_manager=self.config).write_all(
            "song.mp3"
        )

        self.assertEqual(len(results), 2)
        self.assertFalse(any(result.success for result in results))
        self.assertTrue(all("output" in (result.error or "") for result in results))
        mock_ydl_class.assert_not_called()

    def test_import_from_repo_root_exposes_version_and_api_symbols(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import yt2mp3; "
                "from yt2mp3 import ConfigManager, YouTubeDownloader, CLI, url, urls, DownloadRequest, BatchDownloadRequest, DownloadResult; "
                "import yt2mp3.config; "
                "print(yt2mp3.__version__); "
                "print(all([ConfigManager, YouTubeDownloader, CLI, url, urls, DownloadRequest, BatchDownloadRequest, DownloadResult])); "
                "print(yt2mp3.config.ConfigManager is ConfigManager)",
            ],
            cwd=repo_root,
            env=os.environ.copy(),
            check=True,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.stdout.splitlines(), ["1.0.0", "True", "True"])
