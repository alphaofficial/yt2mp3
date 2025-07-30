import unittest
import tempfile
import os
import sys
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from src.yt2mp3.cli import CLI


class TestCLI(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
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
        
        self.assertEqual(args.link, 'https://youtube.com/watch?v=test')
        self.assertIsNone(args.set_download_path)
        self.assertFalse(args.show_config)
    
    @patch('sys.argv', ['yt2mp3.py', '--set-download-path', '/custom/path'])
    def test_parse_arguments_with_set_download_path(self):
        cli = CLI()
        args = cli.parse_arguments()
        
        self.assertEqual(args.set_download_path, '/custom/path')
        self.assertIsNone(args.link)
        self.assertFalse(args.show_config)
    
    @patch('sys.argv', ['yt2mp3.py', '--show-config'])
    def test_parse_arguments_with_show_config(self):
        cli = CLI()
        args = cli.parse_arguments()
        
        self.assertTrue(args.show_config)
        self.assertIsNone(args.link)
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
    def test_run_with_link(self):
        cli = CLI()
        cli.downloader.download = Mock(return_value=True)
        
        cli.run()
        
        cli.downloader.download.assert_called_once_with('https://youtube.com/watch?v=test')
    
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