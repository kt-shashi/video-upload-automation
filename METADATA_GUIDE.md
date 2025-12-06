# Video Metadata Guide

This guide explains how to add titles, descriptions, hashtags, and other metadata to your videos.

## Quick Start

1. **Create a metadata template:**
   ```bash
   python create_metadata_template.py csv
   ```
   This creates `video_metadata.csv` in your project folder.

2. **Edit the CSV file** with your video information:
   - Open `video_metadata.csv` in Excel, Google Sheets, or any text editor
   - Add a row for each video
   - Make sure the `filename` matches your video filename exactly

3. **Run your upload script** - it will automatically use the metadata!

## Metadata File Formats

### CSV Format (Recommended)

The CSV file has these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `filename` | Exact video filename | `my_video.mp4` |
| `title` | YouTube video title | `My Amazing Video Title` |
| `description` | YouTube description (can use `\n` for newlines) | `This is a detailed description.\n\nSubscribe!` |
| `youtube_tags` | Comma-separated tags | `tag1, tag2, tag3` |
| `instagram_caption` | Instagram caption text | `Check out this video! 🎥` |
| `instagram_hashtags` | Hashtags (with or without #) | `#video #amazing #content` |
| `youtube_category` | YouTube category ID | `22` (People & Blogs) |
| `privacy_status` | Privacy setting | `private`, `unlisted`, or `public` |

**Example CSV:**
```csv
filename,title,description,youtube_tags,instagram_caption,instagram_hashtags,youtube_category,privacy_status
video1.mp4,My First Video,This is my first amazing video!\n\nSubscribe for more!,vlog,travel,amazing,Check out my first video! 🎥,#vlog #travel #amazing,22,private
video2.mp4,Second Video,Another great video,vlog,content,Check this out!,#vlog #content,22,unlisted
```

### JSON Format

The JSON file is an array of objects:

```json
[
  {
    "filename": "video1.mp4",
    "title": "My First Video",
    "description": "This is my first amazing video!\n\nSubscribe for more!",
    "youtube_tags": ["vlog", "travel", "amazing"],
    "instagram_caption": "Check out my first video! 🎥",
    "instagram_hashtags": ["#vlog", "#travel", "#amazing"],
    "youtube_category": "22",
    "privacy_status": "private"
  },
  {
    "filename": "video2.mp4",
    "title": "Second Video",
    "description": "Another great video",
    "youtube_tags": ["vlog", "content"],
    "instagram_caption": "Check this out!",
    "instagram_hashtags": ["#vlog", "#content"],
    "youtube_category": "22",
    "privacy_status": "unlisted"
  }
]
```

## How Metadata Works

### Priority Order

1. **Metadata File** (if exists) - Highest priority
2. **Filename** - Extracted from video filename
3. **Config Defaults** - From `upload_config.json`

### Automatic Features

**Title Generation:**
- If no title in metadata, uses filename (cleaned up)
- Removes hashtags, replaces underscores/hyphens with spaces
- Capitalizes words

**Hashtag Extraction:**
- Automatically extracts hashtags from filename (e.g., `video_#travel_#vlog.mp4`)
- Adds hashtags to Instagram caption
- Converts hashtags to YouTube tags (without #)

**Example:**
- Filename: `my_#travel_#vlog_video.mp4`
- Title: `My Travel Vlog Video`
- YouTube Tags: `travel`, `vlog`
- Instagram Hashtags: `#travel`, `#vlog`

## YouTube Categories

Common YouTube category IDs:

| ID | Category |
|----|----------|
| 1 | Film & Animation |
| 2 | Autos & Vehicles |
| 10 | Music |
| 15 | Pets & Animals |
| 17 | Sports |
| 19 | Travel & Events |
| 20 | Gaming |
| 22 | People & Blogs |
| 23 | Comedy |
| 24 | Entertainment |
| 25 | News & Politics |
| 26 | Howto & Style |
| 27 | Education |
| 28 | Science & Technology |

## Tips

1. **Filename Matching**: The `filename` in metadata must match your video filename exactly (case-sensitive on some systems)

2. **Hashtags**: 
   - Instagram supports up to 30 hashtags
   - Use relevant, popular hashtags for better reach
   - Mix popular and niche hashtags

3. **Descriptions**:
   - YouTube descriptions can be long (up to 5000 characters)
   - Use `\n` for line breaks in CSV
   - Include links, timestamps, etc.

4. **Titles**:
   - YouTube titles should be under 100 characters
   - Make them catchy and SEO-friendly
   - Include keywords

5. **Batch Processing**:
   - Create metadata for all videos before running batch upload
   - Videos without metadata will use defaults/filename

## Examples

### Example 1: Simple Video
**Filename:** `sunset_video.mp4`

**Metadata:**
- Title: `Beautiful Sunset Time-lapse`
- Description: `Watch this amazing sunset captured over the ocean.\n\nLocation: California Coast`
- YouTube Tags: `sunset, timelapse, nature, ocean`
- Instagram Caption: `Beautiful sunset! 🌅`
- Instagram Hashtags: `#sunset #timelapse #nature #ocean #california`

### Example 2: Vlog Video
**Filename:** `day_in_life_#vlog_#travel.mp4`

**Metadata:**
- Title: `A Day in My Life - Travel Vlog`
- Description: `Join me for a day exploring the city!\n\nPlaces visited:\n- Central Park\n- Times Square\n\nSubscribe for more travel content!`
- YouTube Tags: `vlog, travel, day in life, new york`
- Instagram Caption: `A day exploring the city! 🏙️`
- Instagram Hashtags: `#vlog #travel #dayinmylife #newyork #explore`

## Troubleshooting

**Metadata not being used?**
- Check that filename in metadata matches video filename exactly
- Ensure metadata file is in the project root directory
- Check `upload_log.txt` for any errors

**Hashtags not appearing?**
- Make sure hashtags start with `#` or are in the hashtags column
- Check that they're included in the `instagram_hashtags` field

**Default values being used instead?**
- Verify your metadata file format is correct (CSV or JSON)
- Check that the filename column matches your video files
- Ensure the metadata file is saved and in the correct location

