# Automated Video Uploader for YouTube and Instagram

This tool automates the process of uploading videos to both YouTube and Instagram simultaneously. It supports local files and can be extended to work with Google Drive.

## ⚠️ Important Notes

### Instagram Disclaimer
- Instagram's official API does not support posting videos to personal accounts
- This tool uses `instagrapi`, an unofficial library that may violate Instagram's Terms of Service
- Use at your own risk - Instagram may temporarily or permanently ban accounts using automation
- Consider using Instagram's official Business API if you have a business account

### YouTube
- Uses official YouTube Data API v3
- Fully compliant with YouTube's Terms of Service
- Requires Google Cloud Console setup

## Prerequisites

1. **Python 3.8+** installed
2. **Google Cloud Project** with YouTube Data API v3 enabled
3. **Instagram account** (personal or business)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. YouTube Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file
   - Rename it to `youtube_credentials.json` and place it in the project directory

### 3. Instagram Setup

1. Edit `upload_config.py` and add your Instagram credentials:
   ```python
   INSTAGRAM_USERNAME = "your_username"
   INSTAGRAM_PASSWORD = "your_password"
   ```

**⚠️ Security Warning**: Consider using environment variables instead of hardcoding passwords:
```python
import os
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
```

### 4. Configuration (Optional)

Edit `upload_config.json` to customize:
- YouTube privacy settings (private/unlisted/public)
- Default descriptions and tags
- Instagram default captions and hashtags
- Upload delay between videos
- Retry attempts

### 5. Video Metadata (Optional but Recommended)

For better control over titles, descriptions, hashtags, etc., create a metadata file:

**Option A: CSV File (Recommended for Excel users)**
```bash
python create_metadata_template.py csv
```
This creates `video_metadata.csv` - edit it with Excel or any spreadsheet app.

**Option B: JSON File**
```bash
python create_metadata_template.py json
```
This creates `video_metadata.json` - edit it with any text editor.

**See `METADATA_GUIDE.md` for detailed instructions on metadata files.**

**If no metadata file exists:**
- Title: Extracted from filename (cleaned up)
- Description: Uses default from config
- Tags: Extracted from filename hashtags (if any) + default tags
- Instagram caption: Default caption + hashtags from filename

## Usage

### Quick Start (Using Assets Folder)

1. Place your videos in the `assets` folder in the project directory
2. Run the upload script:
   ```bash
   python quick_upload.py
   ```
   Or:
   ```bash
   python video_uploader.py
   ```
   The script will automatically detect and use the `assets` folder!

### Upload a Single Video

```bash
python video_uploader.py --video "path/to/video.mp4"
```

### Upload All Videos in a Directory

```bash
python video_uploader.py --directory "path/to/videos"
```

### Upload from Assets Folder Explicitly

```bash
python video_uploader.py --directory assets
```

### Upload Only to YouTube

```bash
python video_uploader.py --directory "path/to/videos" --youtube-only
```

### Upload Only to Instagram

```bash
python video_uploader.py --directory "path/to/videos" --instagram-only
```

### Using as a Python Module

```python
from video_uploader import YouTubeUploader, InstagramUploader, VideoUploadManager

# Initialize uploaders
youtube = YouTubeUploader()
instagram = InstagramUploader("username", "password")

# Create manager
manager = VideoUploadManager(youtube, instagram)

# Upload single video
manager.process_video(
    "video.mp4",
    title="My Video Title",
    description="Video description",
    caption="Instagram caption"
)

# Or process entire directory
manager.process_directory("path/to/videos")
```

## Features

- ✅ **Dual Platform Upload**: Upload to YouTube and Instagram simultaneously
- ✅ **Batch Processing**: Process entire directories of videos
- ✅ **Smart Metadata**: CSV/JSON metadata files for titles, descriptions, hashtags
- ✅ **Hashtag Support**: Automatic hashtag extraction from filenames and metadata
- ✅ **Progress Tracking**: Real-time upload progress and logging
- ✅ **Error Handling**: Robust error handling with retry logic
- ✅ **Upload History**: Tracks all uploads in `upload_history.json`
- ✅ **Configurable**: Customize privacy, descriptions, tags, and more
- ✅ **Rate Limiting**: Built-in delays to avoid platform rate limits

## File Structure

```
automation/
├── video_uploader.py          # Main upload script
├── quick_upload.py             # Simplified upload interface
├── metadata_handler.py         # Metadata management system
├── create_metadata_template.py # Create metadata template files
├── upload_config.py            # Instagram credentials
├── upload_config.json          # Upload settings
├── video_metadata.csv          # Video metadata (CSV format) - optional
├── video_metadata.json         # Video metadata (JSON format) - optional
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── assets/                     # Place your videos here (default folder)
│   └── README.txt             # Instructions for assets folder
├── youtube_credentials.json    # YouTube OAuth credentials (you provide)
├── youtube_token.json          # Auto-generated YouTube token
├── instagram_session.json      # Auto-generated Instagram session
├── upload_history.json         # Upload history log
└── upload_log.txt              # Detailed upload logs
```

## Supported Video Formats

- MP4 (recommended)
- MOV
- AVI
- MKV
- WebM
- FLV

## YouTube Video Limits

- Maximum file size: 256GB
- Maximum duration: 12 hours
- Recommended formats: MP4, MOV, AVI

## Instagram Video Limits

- Maximum duration: 60 seconds for feed posts
- Maximum file size: 100MB
- Recommended format: MP4
- Aspect ratio: 1:1 (square) or 4:5 (vertical)

## Troubleshooting

### YouTube Authentication Issues
- Ensure `youtube_credentials.json` is in the project directory
- Check that YouTube Data API v3 is enabled in Google Cloud Console
- Delete `youtube_token.json` and re-authenticate if needed

### Instagram Login Issues
- Instagram may require 2FA - you may need to disable it temporarily or use an app-specific password
- If you get "Challenge Required", Instagram is asking for verification - complete it manually first
- Delete `instagram_session.json` to force re-login

### Rate Limiting
- Increase `upload_delay` in `upload_config.json` if you hit rate limits
- Instagram has strict rate limits - consider uploading fewer videos per day

### Large File Uploads
- For 50GB+ of content, consider:
  - Processing in smaller batches
  - Using a stable internet connection
  - Running the script during off-peak hours
  - Monitoring disk space for temporary files

## Google Drive Integration (Optional)

To download videos from Google Drive before uploading:

1. Enable Google Drive API in Google Cloud Console
2. Download Drive credentials as `drive_credentials.json`
3. The script will automatically detect and use Drive integration

## Security Best Practices

1. **Never commit credentials to version control**
   - Add `*_credentials.json`, `*_token.json`, `*_session.json` to `.gitignore`
   - Use environment variables for sensitive data

2. **Use separate accounts for testing**
   - Don't risk your main accounts with automation

3. **Monitor your accounts**
   - Check for any warnings or restrictions from platforms

## License

This tool is provided as-is for educational and personal use. Use at your own risk, especially for Instagram automation.

## Support

For issues or questions:
1. Check the logs in `upload_log.txt`
2. Review `upload_history.json` for failed uploads
3. Ensure all credentials are correctly configured

