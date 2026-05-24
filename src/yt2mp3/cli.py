import argparse
import os
import sys

from . import __version__
from .api import url as build_url
from .config import ConfigManager
from .downloader import YouTubeDownloader
from .lifecycle import LifecycleError, uninstall, upgrade


class CLI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.downloader = YouTubeDownloader(self.config_manager)

    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="YouTube to MP3 Converter - Download YouTube videos and convert them to MP3 format",
            prog="yt2mp3",
            epilog="Examples:\n"
            "  %(prog)s --link=\"https://youtube.com/watch?v=xxxxx\"\n"
            "  %(prog)s --link=\"https://youtube.com/watch?v=xxxxx\" --resolution 1080p --audio-quality 320 --output song.mp3\n"
            "  %(prog)s --set-download-path=\"~/Downloads/Music\"\n"
            "  %(prog)s upgrade\n"
            "  %(prog)s uninstall --yes\n"
            "  %(prog)s  (interactive mode)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("command", nargs="?", choices=["upgrade", "uninstall"], help="Lifecycle command")
        parser.add_argument("--version", action="version", version=f"yt2mp3 {__version__}")
        parser.add_argument("--link", metavar="URL", help="YouTube video URL to download and convert to MP3")
        parser.add_argument("--resolution", metavar="HEIGHT", help="Maximum source video height, e.g. 1080p or 720")
        parser.add_argument("--audio-quality", metavar="KBPS", help="MP3 bitrate, e.g. 128, 192, 320")
        parser.add_argument("--output", metavar="FILE", help="Output MP3 filename or path")
        parser.add_argument("--set-download-path", metavar="PATH", help="Set new download directory path and save to configuration file")
        parser.add_argument("--show-config", action="store_true", help="Display current configuration settings")
        parser.add_argument("--keep-video", action="store_true", help="Keep original video file after MP3 conversion")
        parser.add_argument("--no-keep-video", action="store_true", help="Delete original video file after MP3 conversion (default behavior)")
        parser.add_argument("--yes", action="store_true", help="Confirm destructive lifecycle commands")
        return parser.parse_args()

    def interactive_mode(self) -> None:
        print("YouTube to MP3 Converter - Interactive Mode")
        print("=" * 40)

        while True:
            video_url = input("\nEnter YouTube URL (or 'quit' to exit): ").strip()

            if video_url.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if not video_url:
                print("Please enter a valid URL.")
                continue

            info = self.downloader.get_video_info(video_url)
            if info:
                print(f"\nVideo: {info['title']}")
                print(f"Uploader: {info['uploader']}")
                print(f"Duration: {info['duration']} seconds")

                confirm = input("\nDownload this video? (y/n): ").strip().lower()
                if confirm in ["y", "yes"]:
                    self.downloader.download(video_url)
                else:
                    print("Download cancelled.")
            else:
                print("Could not retrieve video information. Try downloading anyway? (y/n): ")
                confirm = input().strip().lower()
                if confirm in ["y", "yes"]:
                    self.downloader.download(video_url)

    def handle_config_commands(self, args: argparse.Namespace) -> bool:
        config_changed = False

        if args.show_config:
            self.config_manager.show_config()
            return True

        if args.set_download_path:
            path = os.path.expanduser(args.set_download_path)
            if os.path.isdir(path) or input(f"Directory '{path}' doesn't exist. Create it? (y/n): ").lower() in ["y", "yes"]:
                try:
                    os.makedirs(path, exist_ok=True)
                    self.config_manager.update_setting("download_path", args.set_download_path)
                    print(f"Download path updated to: {path}")
                    config_changed = True
                except OSError as e:
                    print(f"Error setting download path: {e}")

        if args.keep_video and not args.link:
            self.config_manager.update_setting("keep_video", True)
            print("Video files will now be kept after MP3 conversion")
            config_changed = True

        if args.no_keep_video and not args.link:
            self.config_manager.update_setting("keep_video", False)
            print("Video files will now be deleted after MP3 conversion (default)")
            config_changed = True

        return config_changed or args.set_download_path is not None

    def handle_lifecycle_command(self, args: argparse.Namespace) -> bool:
        if args.command == "upgrade":
            result = upgrade()
            print(result.message)
            return True
        if args.command == "uninstall":
            result = uninstall(yes=args.yes)
            print(result.message)
            return True
        return False

    def run(self) -> None:
        args = self.parse_arguments()

        try:
            if self.handle_lifecycle_command(args):
                return
        except LifecycleError as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc

        if self.handle_config_commands(args):
            return

        if args.link:
            request = build_url(args.link, config_manager=self.config_manager)
            if args.resolution:
                request = request.resolution(args.resolution)
            if args.audio_quality:
                request = request.audio_quality(args.audio_quality)
            if args.keep_video or args.no_keep_video:
                request = request.keep_video(args.keep_video and not args.no_keep_video)
            result = request.write(args.output)
            if not result.success:
                raise SystemExit(1)
        else:
            self.interactive_mode()


def main() -> None:
    try:
        CLI().run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        raise SystemExit(0)
