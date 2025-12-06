# 🎬 Automated Video Uploader for YouTube & Instagram

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![YouTube API](https://img.shields.io/badge/YouTube-API%20v3-red.svg)](https://developers.google.com/youtube/v3)
[![Instagram](https://img.shields.io/badge/Instagram-Unofficial-orange.svg)](https://www.instagram.com/)

> Automate your video uploads to both YouTube and Instagram simultaneously with a single command. Perfect for content creators managing multiple platforms.

## ✨ Features

- 🚀 **Dual Platform Upload** - Upload to YouTube and Instagram simultaneously
- 📦 **Batch Processing** - Process entire directories of videos automatically
- 🏷️ **Smart Metadata** - CSV/JSON support for custom titles, descriptions, and hashtags
- 🔍 **Auto Hashtag Extraction** - Automatically extracts hashtags from filenames
- 📊 **Progress Tracking** - Real-time upload progress and detailed logging
- ⚙️ **Highly Configurable** - Customize privacy, descriptions, tags, and more
- 🔄 **Error Handling** - Robust error handling with automatic retry logic
- 📝 **Upload History** - Complete history of all uploads in JSON format
- ⏱️ **Rate Limiting** - Built-in delays to respect platform rate limits
- ☁️ **Google Drive Support** - Optional integration for downloading videos from Drive

<details>
<summary><h2>🎯 Quick Start</h2></summary>

### Prerequisites

- Python 3.8 or higher
- Google Cloud Project with YouTube Data API v3 enabled
- Instagram account (personal or business)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/automation.git
   cd automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup YouTube**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable **YouTube Data API v3**
   - Create OAuth 2.0 credentials (Desktop app)
   - Download and save as `youtube_credentials.json`
   - **Important**: Add yourself as a test user in OAuth consent screen

4. **Setup Instagram**
   - Edit `upload_config.py` and add your credentials:
     ```python
     INSTAGRAM_USERNAME = "your_username"
     INSTAGRAM_PASSWORD = "your_password"
     ```

5. **Configure settings** (Optional)
   - Edit `upload_config.json` to customize default descriptions, tags, privacy settings, etc.

### Usage

```bash
# Place videos in assets folder and run
python quick_upload.py

# Or upload specific directory
python video_uploader.py --directory "path/to/videos"

# Upload single video
python video_uploader.py --video "video.mp4"
```

</details>

<details>
<summary><h2>📖 Detailed Usage</h2></summary>

### Basic Commands

```bash
# Upload all videos from assets folder (default)
python quick_upload.py

# Upload specific directory
python video_uploader.py --directory "path/to/videos"

# Upload single video
python video_uploader.py --video "video.mp4"

# YouTube only
python video_uploader.py --directory assets --youtube-only

# Instagram only
python video_uploader.py --directory assets --instagram-only
```

### Using Metadata Files

For better control over titles, descriptions, and hashtags:

```bash
# Create CSV template
python create_metadata_template.py csv

# Edit video_metadata.csv with your video information
# Then upload - metadata will be used automatically
python quick_upload.py
```

See [METADATA_GUIDE.md](METADATA_GUIDE.md) for detailed metadata file instructions.

### Configuration

Edit `upload_config.json` to customize default settings:

```json
{
  "youtube": {
    "privacy_status": "public",
    "category_id": "22",
    "default_description": "Your description here",
    "default_tags": ["tag1", "tag2"]
  },
  "instagram": {
    "default_caption": "Your caption",
    "default_hashtags": ["#hashtag1", "#hashtag2"]
  },
  "upload_delay": 5
}
```

</details>

<details>
<summary><h2>📁 Project Structure</h2></summary>

```
automation/
├── video_uploader.py          # Main upload engine
├── quick_upload.py            # Simple CLI interface
├── metadata_handler.py        # Metadata management system
├── create_metadata_template.py # Metadata template generator
├── drive_helper.py            # Google Drive integration helper
├── upload_config.py           # Instagram credentials
├── upload_config.json         # Configuration file
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── METADATA_GUIDE.md          # Detailed metadata guide
├── setup_guide.txt            # Step-by-step setup instructions
└── assets/                    # Place videos here (gitignored)
    └── README.txt            # Instructions for assets folder
```

</details>

<details>
<summary><h2>📊 Supported Formats</h2></summary>

- **Video Formats**: MP4, MOV, AVI, MKV, WebM, FLV
- **Metadata Formats**: CSV, JSON
- **Platforms**: YouTube, Instagram

### Platform Limits

**YouTube:**
- Maximum file size: 256GB
- Maximum duration: 12 hours
- Recommended format: MP4

**Instagram:**
- Maximum duration: 60 seconds for feed posts
- Maximum file size: 100MB
- Recommended format: MP4
- Aspect ratio: 1:1 (square) or 4:5 (vertical)

</details>

<details>
<summary><h2>⚠️ Important Notes</h2></summary>

### Instagram Disclaimer

- This tool uses `instagrapi`, an **unofficial** library
- May violate Instagram's Terms of Service
- Use at your own risk - accounts may be temporarily or permanently restricted
- Consider using Instagram's official Business API for production use

### YouTube

- Uses official YouTube Data API v3
- Fully compliant with YouTube's Terms of Service
- Requires Google Cloud Console setup

</details>

<details>
<summary><h2>🛠️ Troubleshooting</h2></summary>

### Common Issues

| Issue | Solution |
|-------|----------|
| "Access blocked" error | Add your email as test user in Google Cloud Console |
| Instagram login fails | Disable 2FA temporarily or use app-specific password |
| Rate limiting | Increase `upload_delay` in `upload_config.json` |
| Validation errors | Videos still upload successfully - this is a known instagrapi parsing issue |
| Videos marked as failed | Check `upload_log.txt` - validation errors don't mean upload failed |

### Getting Help

1. Check `upload_log.txt` for detailed error messages
2. Review `upload_history.json` for upload status
3. See [setup_guide.txt](setup_guide.txt) for OAuth issues
4. See [METADATA_GUIDE.md](METADATA_GUIDE.md) for metadata questions

</details>

<details>
<summary><h2>🔒 Security Best Practices</h2></summary>

- ✅ Credentials are gitignored (never commit them)
- ✅ Use environment variables for production
- ✅ Use separate test accounts when possible
- ✅ Monitor your accounts for restrictions

</details>

<details>
<summary><h2>📚 Documentation</h2></summary>

- [Setup Guide](setup_guide.txt) - Step-by-step setup instructions
- [Metadata Guide](METADATA_GUIDE.md) - Complete metadata file guide

</details>

<details>
<summary><h2>🤝 Contributing</h2></summary>

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

</details>

<details>
<summary><h2>📄 License</h2></summary>

This project is provided as-is for educational and personal use. Use at your own risk, especially for Instagram automation.

</details>

<details>
<summary><h2>🙏 Acknowledgments</h2></summary>

- [instagrapi](https://github.com/adw0rd/instagrapi) - Instagram API library
- [Google YouTube Data API](https://developers.google.com/youtube/v3) - Official YouTube API

</details>

---

**Made with ❤️ for content creators**
