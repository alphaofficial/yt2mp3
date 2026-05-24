# yt2mp3

Download YouTube videos and convert them to MP3.

## Install with curl

`yt2mp3` release binaries install into `${YT2MP3_HOME:-$HOME/.yt2mp3}/bin/yt2mp3`.

```bash
curl -fsSL https://raw.githubusercontent.com/alphaofficial/yt2mp3/main/install.sh | sh
```

If the installer says the bin directory is not on your `PATH`, add:

```bash
export PATH="$HOME/.yt2mp3/bin:$PATH"
```

### Prerequisite: ffmpeg

`ffmpeg` must be installed for MP3 extraction:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

## Upgrade / uninstall

```bash
yt2mp3 upgrade
yt2mp3 uninstall --yes
```

`uninstall` only removes a safe `.yt2mp3` home directory and refuses suspicious paths.

## Command line usage

```bash
# Download a video
yt2mp3 --link="https://youtube.com/watch?v=xxxxx"

# Download multiple videos sequentially
yt2mp3 --link="https://youtube.com/watch?v=xxxxx" --link="https://youtu.be/yyyyy"
yt2mp3 --links urls.txt

# Limit source video height and set MP3 bitrate
yt2mp3 --link="https://youtube.com/watch?v=xxxxx" --resolution 1080p --audio-quality 320

# Write a specific output file
yt2mp3 --link="https://youtube.com/watch?v=xxxxx" --output song.mp3

# Set download path
yt2mp3 --set-download-path="~/Downloads/Music"

# Keep or delete source video after conversion
yt2mp3 --keep-video
yt2mp3 --no-keep-video

# Show configuration
yt2mp3 --show-config

# Version/help
yt2mp3 --version
yt2mp3 --help
```

`--links` files use one URL per line. Blank lines and full-line comments starting with `#` are ignored; inline `#` text is kept as part of the line. Shared options such as `--resolution`, `--audio-quality`, `--keep-video`, and `--no-keep-video` apply to every URL in a batch. `--output` is only allowed for a single URL because one filename would overwrite multiple downloads.

## Composable Python API

```python
import yt2mp3

result = (
    yt2mp3.url("https://youtube.com/watch?v=xxxxx")
    .resolution("1080p")
    .audio_quality("192")
    .write("song.mp3")
)

batch_results = (
    yt2mp3.urls([
        "https://youtube.com/watch?v=xxxxx",
        "https://youtu.be/yyyyy",
    ])
    .resolution("720p")
    .audio_quality("192")
    .write_all()
)

if not result.success:
    raise RuntimeError(result.error or "download failed")

if any(not item.success for item in batch_results):
    raise RuntimeError("one or more downloads failed")
```

- `.resolution("1080p")` / `.resolution("1080")` limits the source video selector to `height<=1080` while MP3 extraction remains the default.
- `.audio_quality("320")` controls MP3 bitrate.
- `.write()` writes to the configured download directory using the configured yt-dlp filename template.
- `.write("song.mp3")` writes that MP3 name inside the configured download directory unless an absolute path is supplied.
- `yt2mp3.urls([...]).resolution(...).audio_quality(...).write_all()` downloads URLs sequentially and returns one `DownloadResult` per URL.

## Configuration

The default config is `${YT2MP3_HOME:-$HOME/.yt2mp3}/config.json`:

```json
{
  "download_path": "~/Downloads",
  "audio_quality": "192",
  "filename_format": "%(title)s.%(ext)s",
  "keep_video": false,
  "resolution": "480"
}
```

Explicit `ConfigManager(config_path)` usage is still supported for tests and embedding.

## Development

This project uses [uv](https://github.com/astral-sh/uv). Do not install project dependencies globally.

```bash
uv sync
uv run pytest
uv run yt2mp3 --help
uv build
```
