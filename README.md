# yt2mp3

Downloads YouTube videos and convert them to MP3 format.

## Installation

### Option 1: Install as Package (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/yt2mp3.git
cd yt2mp3

# Install with uv (fast)
uv sync

# Install the package
uv pip install -e .

# Now you can use yt2mp3 from anywhere
yt2mp3 --help
```

### Option 2: Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/yt2mp3.git
cd yt2mp3

# Install dependencies with uv
uv sync

# Run directly
uv run python yt2mp3.py --help
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
| Bitrate | Quality Level    | Approx. File Size | Recommended Use                |
|---------|------------------|-------------------|--------------------------------|
| `"96"`  | Low              | ~0.7 MB/min       | Voice, podcasts, save space    |
| `"128"` | Standard         | ~1 MB/min         | General listening, streaming   |
| `"192"` | High (**Default**) | ~1.4 MB/min     | Music, balanced quality/size   |
| `"256"` | Very High        | ~1.9 MB/min       | Audiophile, high fidelity      |
| `"320"` | Maximum          | ~2.4 MB/min       | Best possible MP3 quality      |

**To change audio quality:** Edit `config.json` and modify the `"audio_quality"` value.


## Development

### Key Commands
```bash
# Install/update dependencies
uv sync

# Run tests in virtual environment
uv run pytest

# Add new dependencies
uv add <package>

# Build distribution packages
uv build
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_config.py
```


## Requirements

- Python 3.8+
- yt-dlp (YouTube downloader)
- ffmpeg (audio conversion)

**Note:** This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.