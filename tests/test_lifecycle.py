import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.yt2mp3.config import ConfigManager, get_yt2mp3_home
from src.yt2mp3.lifecycle import (
    LifecycleError,
    artifact_name,
    default_install_path,
    uninstall,
    upgrade,
)


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name) / ".yt2mp3"
        self.bin_dir = self.home / "bin"
        self.bin_dir.mkdir(parents=True)
        self.binary = self.bin_dir / "yt2mp3"
        self.binary.write_text("old")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_config_defaults_to_yt2mp3_home_config(self):
        with patch.dict(os.environ, {"YT2MP3_HOME": str(self.home)}):
            manager = ConfigManager()
            self.assertEqual(manager.config_file, self.home / "config.json")
            self.assertTrue(manager.config_file.exists())

    def test_get_yt2mp3_home_uses_environment_override(self):
        with patch.dict(os.environ, {"YT2MP3_HOME": str(self.home)}):
            self.assertEqual(get_yt2mp3_home(), self.home)

    def test_default_install_path(self):
        self.assertEqual(default_install_path(self.home), self.binary)

    @patch("src.yt2mp3.lifecycle.platform.machine", return_value="arm64")
    @patch("src.yt2mp3.lifecycle.platform.system", return_value="Darwin")
    def test_artifact_name_detects_macos_arm64(self, mock_system, mock_machine):
        self.assertEqual(artifact_name(), "yt2mp3-darwin-arm64")

    @patch("src.yt2mp3.lifecycle.platform.machine", return_value="aarch64")
    @patch("src.yt2mp3.lifecycle.platform.system", return_value="Linux")
    def test_artifact_name_detects_linux_arm64(self, mock_system, mock_machine):
        self.assertEqual(artifact_name(), "yt2mp3-linux-arm64")

    @patch("src.yt2mp3.lifecycle.platform.system", return_value="Windows")
    def test_artifact_name_rejects_windows_without_release_asset(self, mock_system):
        with self.assertRaises(LifecycleError):
            artifact_name()

    @patch("src.yt2mp3.lifecycle.platform.system", return_value="Linux")
    @patch("src.yt2mp3.lifecycle.subprocess.run")
    def test_upgrade_downloads_to_temp_and_replaces_binary(self, mock_run, mock_system):
        def fake_run(cmd, check, **kwargs):
            if "-o" not in cmd:
                return None
            output = Path(cmd[cmd.index("-o") + 1])
            output.write_text("new")

        mock_run.side_effect = fake_run

        result = upgrade(home=self.home, repo="owner/repo")

        self.assertTrue(result.success)
        self.assertEqual(self.binary.read_text(), "new")
        self.assertIn("yt2mp3-", result.artifact)
        self.assertTrue(os.access(self.binary, os.X_OK))
        called = " ".join(mock_run.call_args_list[0].args[0])
        self.assertIn("https://github.com/owner/repo/releases/latest/download/", called)

    def test_uninstall_removes_safe_home(self):
        result = uninstall(home=self.home, yes=True)
        self.assertTrue(result.success)
        self.assertFalse(self.home.exists())

    def test_uninstall_refuses_suspicious_path(self):
        with self.assertRaises(LifecycleError):
            uninstall(home=Path("/"), yes=True)
