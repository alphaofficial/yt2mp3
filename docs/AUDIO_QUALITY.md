# 🎵 Audio Quality Configuration Guide

## 📊 Understanding Audio Quality Settings

The `audio_quality` setting in your `config.json` file controls the **bitrate** of the final MP3 files. This determines the balance between audio quality and file size.

### Current Default Setting
```json
{
  "audio_quality": "192"
}
```

## 🎚️ Supported Quality Levels

### Quality Comparison Table

| Bitrate | Quality Level | File Size (per minute) | Use Case | Recommended For |
|---------|---------------|------------------------|----------|-----------------|
| `"96"`  | Low Quality   | ~0.7 MB | Voice content, podcasts | Speech, saving storage space |
| `"128"` | Good Quality  | ~1.0 MB | General listening | Casual music, mobile devices |
| `"192"` | High Quality  | ~1.4 MB | **Default setting** | Most music, balanced quality/size |
| `"256"` | Very High     | ~1.9 MB | Audiophile quality | High-end audio equipment |
| `"320"` | Maximum       | ~2.4 MB | Best possible MP3 | Professional use, archival |

### Quality Descriptions

#### **96 kbps - Low Quality**
- **Best for:** Podcasts, audiobooks, voice recordings
- **Pros:** Very small file sizes, fast downloads
- **Cons:** Noticeable compression artifacts in music
- **Example:** 4-minute song = ~2.9 MB

#### **128 kbps - Good Quality**
- **Best for:** General music listening, streaming
- **Pros:** Good balance for casual listening
- **Cons:** Some compression artifacts audible on good speakers
- **Example:** 4-minute song = ~3.8 MB

#### **192 kbps - High Quality (Default)**
- **Best for:** Most music collections, daily listening
- **Pros:** Excellent quality-to-size ratio, suitable for all genres
- **Cons:** Slightly larger files than 128 kbps
- **Example:** 4-minute song = ~5.8 MB

#### **256 kbps - Very High Quality**
- **Best for:** High-quality music collections, good headphones
- **Pros:** Near-CD quality, minimal compression artifacts
- **Cons:** Larger file sizes
- **Example:** 4-minute song = ~7.7 MB

#### **320 kbps - Maximum Quality**
- **Best for:** Audiophile collections, professional use
- **Pros:** Maximum MP3 quality, indistinguishable from source
- **Cons:** Largest file sizes
- **Example:** 4-minute song = ~9.6 MB

## 🔧 How to Change Audio Quality

### Method 1: Edit Configuration File (Recommended)

1. **Locate the config file:**
   ```bash
   # The config.json file is in your project directory
   ls config.json
   ```

2. **Edit the file:**
   ```bash
   # Using nano
   nano config.json
   
   # Using VS Code
   code config.json
   
   # Using any text editor
   open -a TextEdit config.json
   ```

3. **Modify the audio_quality value:**
   ```json
   {
     "download_path": "/Users/albert/Downloads",
     "audio_quality": "320",  ← Change this value
     "filename_format": "%(title)s.%(ext)s",
     "keep_video": false
   }
   ```

4. **Save the file and test:**
   ```bash
   python yt2mp3.py --show-config
   python yt2mp3.py --link="https://youtube.com/watch?v=test"
   ```

### Method 2: Programmatic Update (Advanced)

If you want to add a CLI option for changing audio quality, you can modify the code:

**Add to `src/yt2mp3/cli.py`:**
```python
# In parse_arguments method
parser.add_argument(
    "--set-audio-quality",
    metavar="BITRATE",
    choices=["96", "128", "192", "256", "320"],
    help="Set MP3 audio quality bitrate (96, 128, 192, 256, 320)"
)

# In handle_config_commands method
if args.set_audio_quality:
    self.config_manager.update_setting("audio_quality", args.set_audio_quality)
    print(f"Audio quality updated to: {args.set_audio_quality} kbps")
    return True
```

## 📁 File Size Impact Examples

### Storage Requirements for Different Collections

#### **Small Collection (50 songs, 4 minutes average)**
- **96 kbps:** ~145 MB total
- **128 kbps:** ~190 MB total  
- **192 kbps:** ~290 MB total (default)
- **256 kbps:** ~385 MB total
- **320 kbps:** ~480 MB total

#### **Large Collection (1000 songs, 4 minutes average)**
- **96 kbps:** ~2.9 GB total
- **128 kbps:** ~3.8 GB total
- **192 kbps:** ~5.8 GB total (default)
- **256 kbps:** ~7.7 GB total
- **320 kbps:** ~9.6 GB total

## 🎯 Recommended Settings by Use Case

### **🎵 Music Enthusiast (Recommended)**
```json
"audio_quality": "192"
```
- Perfect for most music listening
- Great balance of quality and storage
- Suitable for all playback devices

### **🎧 Audiophile Setup**
```json
"audio_quality": "320"
```
- Maximum MP3 quality
- For high-end headphones/speakers
- When storage space isn't a concern

### **📱 Mobile/Limited Storage**
```json
"audio_quality": "128"
```
- Smaller files for mobile devices
- Good quality for earbuds/car audio
- Saves significant storage space

### **🎙️ Podcasts/Speech Content**
```json
"audio_quality": "96"
```
- Optimized for voice clarity
- Minimal file sizes
- Perfect for spoken content

### **💾 Archival/Professional**
```json
"audio_quality": "320"
```
- Best possible MP3 quality
- Future-proof for better equipment
- Professional audio work

## 🔍 Technical Details

### How the Setting Works

The `audio_quality` value is passed to **FFmpeg** during conversion:

```python
# In src/yt2mp3/downloader.py
'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': self.config.config["audio_quality"],  # ← Your setting
}]
```

### Quality Limitations

1. **Source Quality:** The final quality cannot exceed the original YouTube audio
2. **Codec Efficiency:** MP3 at 320 kbps ≈ CD quality for most listeners
3. **Diminishing Returns:** Above 256 kbps, improvements are minimal for most people

## 🧪 Testing Different Qualities

### Quality Comparison Test
```bash
# 1. Set to low quality
# Edit config.json: "audio_quality": "128"
python yt2mp3.py --link="https://youtube.com/watch?v=SHORT_SONG"

# 2. Set to high quality  
# Edit config.json: "audio_quality": "320"
python yt2mp3.py --link="https://youtube.com/watch?v=SAME_SONG"

# 3. Compare files
ls -lh ~/Downloads/*.mp3
# Listen to both files with good headphones
```

### A/B Testing Tips
- Use the same song for comparison
- Test with different music genres (classical, rock, electronic)
- Use quality headphones or speakers
- Test on different playback devices

## ⚠️ Important Notes

### Configuration Format
- **Always use quotes:** `"192"` not `192`
- **Valid values only:** 96, 128, 192, 256, 320
- **Case sensitive:** Use exact values as shown

### Common Mistakes
```json
// ❌ Wrong - no quotes
"audio_quality": 192

// ❌ Wrong - invalid value  
"audio_quality": "200"

// ✅ Correct
"audio_quality": "192"
```

### Performance Considerations
- **Higher quality = longer conversion time**
- **Network speed doesn't change** (downloads same source)
- **Storage requirements scale linearly** with quality

## 🎵 Quality Recommendations by Genre

### **Classical/Orchestral Music**
```json
"audio_quality": "256"  // or "320"
```
- Complex harmonies benefit from higher bitrates
- Wide dynamic range requires quality preservation

### **Rock/Pop Music**
```json
"audio_quality": "192"  // Default is perfect
```
- Good balance for compressed modern music
- Most rock/pop is mastered for lower bitrates anyway

### **Electronic/EDM**
```json
"audio_quality": "256"  // or "320"
```
- Synthesized sounds and bass benefit from higher quality
- Electronic music often has wide frequency range

### **Podcasts/Talk Shows**
```json
"audio_quality": "96"   // or "128"
```
- Voice content doesn't need high bitrates
- Significant storage savings

This guide should help you choose the perfect audio quality setting for your needs!