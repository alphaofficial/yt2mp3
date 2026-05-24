import unittest
import tempfile
import os
import shutil
import sys
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from src.yt2mp3.cli import CLI


class TestCLI(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.env_patcher = patch.dict(os.environ, {"YT2MP3_HOME": self.temp_dir})
        self.env_patcher.start()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
    def tearDown(self):
        self.env_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.yt2mp3.cli.ConfigManager')
    @patch('src.yt2mp3.cli.YouTubeDownloader')
    def test_cli_initialization(self, mock_downloader_class, mock_config_class):
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader
        
        cli = CLI()
        
        mock_config_class.assert_called_once()
        mock_downloader_class.assert_called_once_with(mock_config)
        self.assertEqual(cli.config_manager, mock_config)
        self.assertEqual(cli.downloader, mock_downloader)
    
    @patch('sys.argv', ['yt2mp3.py', '--link', 'https://youtube.com/watch?v=test'])
    def test_parse_arguments_with_link(self):
        cli = CLI()
        args = cli.parse_arguments()
        
        self.assertEqual(args.link, ['https://youtube.com/watch?v=test'])
        self.assertIsNone(args.links)
        self.assertIsNone(args.set_download_path)
        self.assertFalse(args.show_config)
    
    @patch('sys.argv', ['yt2mp3.py', '--set-download-path', '/custom/path'])
    def test_parse_arguments_with_set_download_path(self):
        cli = CLI()
        args = cli.parse_arguments()
        
        self.assertEqual(args.set_download_path, '/custom/path')
        self.assertIsNone(args.link)
        self.assertIsNone(args.links)
        self.assertFalse(args.show_config)
    
    @patch('sys.argv', ['yt2mp3.py', '--show-config'])
    def test_parse_arguments_with_show_config(self):
        cli = CLI()
        args = cli.parse_arguments()
        
        self.assertTrue(args.show_config)
        self.assertIsNone(args.link)
        self.assertIsNone(args.links)
        self.assertIsNone(args.set_download_path)
    
    @patch('builtins.input', side_effect=['https://youtube.com/watch?v=test', 'y', 'quit'])
    @patch('builtins.print')
    def test_interactive_mode_download_video(self, mock_print, mock_input):
        cli = CLI()
        cli.downloader.get_video_info = Mock(return_value={
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'duration': 180
        })
        cli.downloader.download = Mock(return_value=True)
        
        cli.interactive_mode()
        
        cli.downloader.get_video_info.assert_called_with('https://youtube.com/watch?v=test')
        cli.downloader.download.assert_called_with('https://youtube.com/watch?v=test')
    
    @patch('builtins.input', side_effect=['https://youtube.com/watch?v=test', 'n', 'quit'])
    @patch('builtins.print')
    def test_interactive_mode_cancel_download(self, mock_print, mock_input):
        cli = CLI()
        cli.downloader.get_video_info = Mock(return_value={
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'duration': 180
        })
        cli.downloader.download = Mock()
        
        cli.interactive_mode()
        
        cli.downloader.get_video_info.assert_called_with('https://youtube.com/watch?v=test')
        cli.downloader.download.assert_not_called()
        mock_print.assert_any_call("Download cancelled.")
    
    @patch('builtins.input', side_effect=['', 'quit'])
    @patch('builtins.print')
    def test_interactive_mode_empty_url(self, mock_print, mock_input):
        cli = CLI()
        
        cli.interactive_mode()
        
        mock_print.assert_any_call("Please enter a valid URL.")
    
    @patch('builtins.input', side_effect=['https://youtube.com/watch?v=test', 'y', 'quit'])
    @patch('builtins.print')
    def test_interactive_mode_no_video_info_download_anyway(self, mock_print, mock_input):
        cli = CLI()
        cli.downloader.get_video_info = Mock(return_value=None)
        cli.downloader.download = Mock(return_value=True)
        
        cli.interactive_mode()
        
        cli.downloader.download.assert_called_with('https://youtube.com/watch?v=test')
    
    def test_handle_config_commands_show_config(self):
        cli = CLI()
        cli.config_manager.show_config = Mock()
        
        args = Mock()
        args.show_config = True
        args.set_download_path = None
        args.keep_video = False
        args.no_keep_video = False
        
        result = cli.handle_config_commands(args)
        
        self.assertTrue(result)
        cli.config_manager.show_config.assert_called_once()
    
    @patch('os.path.isdir', return_value=True)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_handle_config_commands_set_download_path_existing_dir(self, mock_print, mock_makedirs, mock_isdir):
        cli = CLI()
        cli.config_manager.update_setting = Mock()
        
        args = Mock()
        args.show_config = False
        args.set_download_path = '/new/path'
        args.keep_video = False
        args.no_keep_video = False
        
        result = cli.handle_config_commands(args)
        
        self.assertTrue(result)
        mock_makedirs.assert_called_once_with('/new/path', exist_ok=True)
        cli.config_manager.update_setting.assert_called_once_with("download_path", '/new/path')
    
    @patch('os.path.isdir', return_value=False)
    @patch('builtins.input', return_value='n')
    def test_handle_config_commands_set_download_path_decline_create(self, mock_input, mock_isdir):
        cli = CLI()
        cli.config_manager.update_setting = Mock()
        
        args = Mock()
        args.show_config = False
        args.set_download_path = '/new/path'
        args.keep_video = False
        args.no_keep_video = False
        
        result = cli.handle_config_commands(args)
        
        self.assertTrue(result)
        cli.config_manager.update_setting.assert_not_called()
    
    def test_handle_config_commands_no_config_commands(self):
        cli = CLI()
        
        args = Mock()
        args.show_config = False
        args.set_download_path = None
        args.keep_video = False
        args.no_keep_video = False
        
        result = cli.handle_config_commands(args)
        
        self.assertFalse(result)
    
    @patch('sys.argv', ['yt2mp3.py', '--link', 'https://youtube.com/watch?v=test'])
    @patch('src.yt2mp3.cli.build_url')
    def test_run_with_link(self, mock_build_url):
        cli = CLI()
        mock_request = Mock()
        mock_request.write.return_value = Mock(success=True)
        mock_build_url.return_value = mock_request
        
        cli.run()
        
        mock_build_url.assert_called_once_with('https://youtube.com/watch?v=test', config_manager=cli.config_manager)
        mock_request.write.assert_called_once_with(None)

    @patch('sys.argv', ['yt2mp3.py', '--link', 'https://youtube.com/watch?v=one', '--link', 'https://youtu.be/two', '--resolution', '720p', '--audio-quality', '128'])
    @patch('src.yt2mp3.cli.build_urls')
    def test_run_with_repeated_links(self, mock_build_urls):
        cli = CLI()
        mock_request = Mock()
        mock_request.resolution.return_value = mock_request
        mock_request.audio_quality.return_value = mock_request
        mock_request.write_all.return_value = [Mock(success=True), Mock(success=True)]
        mock_build_urls.return_value = mock_request

        cli.run()

        mock_build_urls.assert_called_once_with(
            ['https://youtube.com/watch?v=one', 'https://youtu.be/two'], config_manager=cli.config_manager
        )
        mock_request.resolution.assert_called_once_with('720p')
        mock_request.audio_quality.assert_called_once_with('128')
        mock_request.write_all.assert_called_once_with()

    @patch('sys.argv', ['yt2mp3.py', '--links', 'urls.txt'])
    @patch('src.yt2mp3.cli.build_urls')
    def test_run_with_links_file_ignores_blanks_and_full_line_comments(self, mock_build_urls):
        cli = CLI()
        links_file = os.path.join(self.temp_dir, 'urls.txt')
        with open(links_file, 'w', encoding='utf-8') as file:
            file.write('\n# comment\nhttps://youtube.com/watch?v=one\n  https://youtu.be/two # not inline comment\n')
        with patch('sys.argv', ['yt2mp3.py', '--links', links_file]):
            mock_request = Mock()
            mock_request.write_all.return_value = [Mock(success=True), Mock(success=True)]
            mock_build_urls.return_value = mock_request

            cli.run()

        mock_build_urls.assert_called_once_with(
            ['https://youtube.com/watch?v=one', 'https://youtu.be/two # not inline comment'], config_manager=cli.config_manager
        )
        mock_request.write_all.assert_called_once_with()

    @patch('src.yt2mp3.cli.build_url')
    def test_run_with_missing_links_file_exits_cleanly(self, mock_build_url):
        cli = CLI()
        missing_file = os.path.join(self.temp_dir, 'missing-urls.txt')
        cli.interactive_mode = Mock()

        with patch('sys.argv', ['yt2mp3.py', '--links', missing_file]), patch('sys.stderr', new_callable=StringIO) as stderr:
            with self.assertRaises(SystemExit) as context:
                cli.run()

        self.assertEqual(context.exception.code, 2)
        self.assertIn("Error reading --links file", stderr.getvalue())
        self.assertIn(missing_file, stderr.getvalue())
        mock_build_url.assert_not_called()
        cli.interactive_mode.assert_not_called()

    @patch('src.yt2mp3.cli.build_url')
    def test_run_with_empty_links_file_exits_without_interactive_mode(self, mock_build_url):
        cli = CLI()
        links_file = os.path.join(self.temp_dir, 'empty-urls.txt')
        with open(links_file, 'w', encoding='utf-8') as file:
            file.write('\n# comment\n   # another comment\n\n')
        cli.interactive_mode = Mock()

        with patch('sys.argv', ['yt2mp3.py', '--links', links_file]), patch('sys.stderr', new_callable=StringIO) as stderr:
            with self.assertRaises(SystemExit) as context:
                cli.run()

        self.assertEqual(context.exception.code, 2)
        self.assertIn("no URLs found in --links file", stderr.getvalue())
        self.assertIn(links_file, stderr.getvalue())
        mock_build_url.assert_not_called()
        cli.interactive_mode.assert_not_called()

    @patch('sys.argv', ['yt2mp3.py', '--link', 'https://youtube.com/watch?v=one', '--link', 'https://youtu.be/two', '--output', 'song.mp3'])
    @patch('src.yt2mp3.cli.build_urls')
    def test_run_rejects_output_with_multiple_links(self, mock_build_urls):
        cli = CLI()

        with self.assertRaises(SystemExit) as context:
            cli.run()

        self.assertEqual(context.exception.code, 2)
        mock_build_urls.assert_not_called()

    @patch('sys.argv', ['yt2mp3.py', '--link', 'https://youtube.com/watch?v=one', '--link', 'https://youtu.be/two'])
    @patch('src.yt2mp3.cli.build_urls')
    def test_run_with_batch_exits_nonzero_if_any_download_fails(self, mock_build_urls):
        cli = CLI()
        mock_request = Mock()
        mock_request.write_all.return_value = [Mock(success=True), Mock(success=False)]
        mock_build_urls.return_value = mock_request

        with self.assertRaises(SystemExit) as context:
            cli.run()

        self.assertEqual(context.exception.code, 1)

    @patch('sys.argv', ['yt2mp3.py', '--link', 'https://youtube.com/watch?v=test', '--keep-video'])
    @patch('src.yt2mp3.cli.build_url')
    def test_run_with_link_and_keep_video_downloads_with_request_override(self, mock_build_url):
        cli = CLI()
        cli.config_manager.update_setting = Mock()
        mock_request = Mock()
        mock_request.keep_video.return_value = mock_request
        mock_request.write.return_value = Mock(success=True)
        mock_build_url.return_value = mock_request

        cli.run()

        cli.config_manager.update_setting.assert_not_called()
        mock_build_url.assert_called_once_with('https://youtube.com/watch?v=test', config_manager=cli.config_manager)
        mock_request.keep_video.assert_called_once_with(True)
        mock_request.write.assert_called_once_with(None)

    @patch('sys.argv', ['yt2mp3.py', '--link', 'https://youtube.com/watch?v=test', '--no-keep-video'])
    @patch('src.yt2mp3.cli.build_url')
    def test_run_with_link_and_no_keep_video_downloads_with_request_override(self, mock_build_url):
        cli = CLI()
        cli.config_manager.update_setting = Mock()
        mock_request = Mock()
        mock_request.keep_video.return_value = mock_request
        mock_request.write.return_value = Mock(success=True)
        mock_build_url.return_value = mock_request

        cli.run()

        cli.config_manager.update_setting.assert_not_called()
        mock_build_url.assert_called_once_with('https://youtube.com/watch?v=test', config_manager=cli.config_manager)
        mock_request.keep_video.assert_called_once_with(False)
        mock_request.write.assert_called_once_with(None)

    @patch('sys.argv', ['yt2mp3.py', '--keep-video'])
    def test_run_without_link_and_keep_video_updates_config(self):
        cli = CLI()
        cli.config_manager.update_setting = Mock()
        cli.interactive_mode = Mock()

        cli.run()

        cli.config_manager.update_setting.assert_called_once_with("keep_video", True)
        cli.interactive_mode.assert_not_called()

    @patch('sys.argv', ['yt2mp3.py', '--no-keep-video'])
    def test_run_without_link_and_no_keep_video_updates_config(self):
        cli = CLI()
        cli.config_manager.update_setting = Mock()
        cli.interactive_mode = Mock()

        cli.run()

        cli.config_manager.update_setting.assert_called_once_with("keep_video", False)
        cli.interactive_mode.assert_not_called()
    
    @patch('sys.argv', ['yt2mp3.py', '--show-config'])
    def test_run_with_config_command(self):
        cli = CLI()
        cli.config_manager.show_config = Mock()
        cli.interactive_mode = Mock()
        
        cli.run()
        
        cli.config_manager.show_config.assert_called_once()
        cli.interactive_mode.assert_not_called()
    
    @patch('sys.argv', ['yt2mp3.py'])
    def test_run_interactive_mode(self):
        cli = CLI()
        cli.interactive_mode = Mock()
        
        cli.run()
        
        cli.interactive_mode.assert_called_once()


if __name__ == '__main__':
    unittest.main()