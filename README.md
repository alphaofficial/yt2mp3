# YouTube to MP3 Converter

A simple, interactive Python program to download YouTube videos and convert them to MP3 format.

## Features

- 🎵 **Audio-first downloads** - Prioritizes audio-only streams for faster downloads
- 💻 **Command-line interface** with `--link` parameter
- 🖥️ **Interactive mode** for easy use
- ⚙️ **Configurable settings** via JSON config file
- 📁 **Flexible download location** - Default Downloads folder, easily changeable
- 🎛️ **Video retention control** - Choose to keep or delete original video files
- 🔧 **CLI config management** - Update settings from command line
- 🎚️ **Customizable audio quality** - MP3 bitrate control

## Installation

### Option 1: Install as Package (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/yt2mp3.git
cd yt2mp3

# Install the package
pip install -e .

# Now you can use yt2mp3 from anywhere
yt2mp3 --help
```

### Option 2: Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/yt2mp3.git
cd yt2mp3

# Install dependencies
pip install -r requirements.txt

# Run directly
python yt2mp3.py --help
```

### Prerequisites
Make sure you have `ffmpeg` installed (required for audio conversion):

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Usage

### Command Line Mode
```bash
# Download a video
yt2mp3 --link="https://youtube.com/watch?v=xxxxx"

# Set download path
yt2mp3 --set-download-path="~/Downloads/Music"

# Keep video files after conversion
yt2mp3 --keep-video

# Delete video files after conversion (default)
yt2mp3 --no-keep-video

# Show current configuration
yt2mp3 --show-config

# Get help
yt2mp3 --help
```

### Interactive Mode
```bash
# Start interactive mode
yt2mp3
```

## Configuration

The program uses a `config.json` file with the following default settings:

```json
{
  "download_path": "~/Downloads",
  "audio_quality": "192",
  "filename_format": "%(title)s.%(ext)s",
  "keep_video": false
}
```

**Configuration Options:**
- `download_path`: Where to save MP3 files (and videos if kept)
- `audio_quality`: MP3 bitrate in kbps - controls quality vs file size balance
- `filename_format`: How to name downloaded files (yt-dlp format)
- `keep_video`: Whether to keep original video files after MP3 conversion

### Audio Quality Settings

The `audio_quality` setting controls the MP3 bitrate (quality vs file size):

| Bitrate | Quality Level | File Size | Use Case |
|---------|---------------|-----------|----------|
| `"96"`  | Low Quality   | ~0.7 MB/min | Voice, podcasts, saving space |
| `"128"` | Good Quality  | ~1 MB/min | General listening, streaming |
| `"192"` | High Quality  | ~1.4 MB/min | **Default** - Great for music |
| `"256"` | Very High     | ~1.9 MB/min | Audiophile quality |
| `"320"` | Maximum       | ~2.4 MB/min | Best possible MP3 quality |

**To change audio quality:** Edit `config.json` and modify the `"audio_quality"` value.

## Project Structure

```
yt2mp3/
├── src/
│   └── yt2mp3/
│       ├── __init__.py
│       ├── config.py      # Configuration management
│       ├── downloader.py  # YouTube download logic
│       └── cli.py         # Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_downloader.py
│   └── test_cli.py
├── docs/                  # Documentation
├── yt2mp3.py             # Main entry point
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
├── README.md
└── LICENSE
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_config.py
```

### Code Structure
The project follows a modular OOP design:

- **ConfigManager**: Handles JSON configuration file operations
- **YouTubeDownloader**: Manages yt-dlp operations and MP3 conversion
- **CLI**: Handles command-line interface and user interaction

## Requirements

- Python 3.7+
- yt-dlp (YouTube downloader)
- ffmpeg (audio conversion)

## License

MIT License - see [LICENSE](LICENSE) file for details.