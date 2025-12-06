"""
Automated Video Uploader for YouTube and Instagram
Supports local files and Google Drive integration
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import time

# Metadata handler
try:
    from metadata_handler import MetadataHandler
except ImportError:
    MetadataHandler = None
    logger.warning("metadata_handler not available. Metadata features will be limited.")

# YouTube imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from googleapiclient.errors import HttpError

# Instagram imports (using instagrapi - unofficial but functional)
try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, ChallengeRequired
except ImportError:
    print("Warning: instagrapi not installed. Instagram uploads will be disabled.")
    Client = None

# Google Drive imports (optional)
try:
    from googleapiclient.discovery import build as drive_build
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YouTubeUploader:
    """Handles YouTube video uploads using YouTube Data API v3"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    
    def __init__(self, credentials_file: str = 'youtube_credentials.json'):
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        token_file = 'youtube_token.json'
        
        # Load existing token
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"YouTube credentials file not found: {self.credentials_file}\n"
                        "Please download it from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=creds)
        logger.info("YouTube authentication successful")
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        privacy_status: str = "private",  # "private", "unlisted", "public"
        category_id: str = "22"  # People & Blogs
    ) -> Optional[str]:
        """
        Upload video to YouTube
        
        Returns video ID if successful, None otherwise
        """
        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            logger.info(f"Uploading to YouTube: {title}")
            insert_request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"YouTube upload progress: {progress}%")
            
            if 'id' in response:
                video_id = response['id']
                logger.info(f"YouTube upload successful! Video ID: {video_id}")
                return video_id
            else:
                logger.error(f"YouTube upload failed: {response}")
                return None
                
        except HttpError as e:
            logger.error(f"YouTube upload error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during YouTube upload: {e}")
            return None


class InstagramUploader:
    """Handles Instagram video uploads using instagrapi"""
    
    def __init__(self, username: str, password: str, session_file: str = 'instagram_session.json'):
        if Client is None:
            raise ImportError("instagrapi is not installed. Install it with: pip install instagrapi")
        
        self.username = username
        self.password = password
        self.session_file = session_file
        self.client = Client()
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Instagram"""
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                self.client.load_settings(self.session_file)
                try:
                    self.client.login(self.username, self.password)
                    logger.info("Instagram authentication successful (using saved session)")
                    return
                except (LoginRequired, ChallengeRequired):
                    logger.warning("Instagram session expired, re-authenticating...")
            
            # New login
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            logger.info("Instagram authentication successful")
            
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            raise
    
    def upload_video(
        self,
        video_path: str,
        caption: str = "",
        thumbnail_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload video to Instagram
        
        Returns media ID if successful, None otherwise
        """
        try:
            logger.info(f"Uploading to Instagram: {caption[:50]}...")
            
            # Instagram requires video to be less than 60 seconds for feed posts
            # For longer videos, you might need to use IGTV or Reels
            
            media_id = self.client.clip_upload(
                video_path,
                caption=caption,
                thumbnail=thumbnail_path
            )
            
            logger.info(f"Instagram upload successful! Media ID: {media_id}")
            return media_id
            
        except Exception as e:
            error_str = str(e)
            # Check if it's a validation error that happens after successful upload
            # These errors often occur when the video is already uploaded but response parsing fails
            if "validation error" in error_str.lower() or "audio_filter_infos" in error_str or "list_type" in error_str:
                logger.warning(f"Instagram upload completed but response validation failed: {e}")
                logger.info("Video may have been uploaded successfully despite validation error")
                # Return a special marker to indicate upload likely succeeded
                return "uploaded_with_validation_error"
            else:
                logger.error(f"Instagram upload error: {e}")
                return None


class GoogleDriveDownloader:
    """Downloads videos from Google Drive"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, credentials_file: str = 'drive_credentials.json'):
        self.credentials_file = credentials_file
        self.service = None
        if DRIVE_AVAILABLE:
            self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        token_file = 'drive_token.json'
        
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.warning("Google Drive credentials not found. Skipping Drive integration.")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        if creds:
            self.service = drive_build('drive', 'v3', credentials=creds)
            logger.info("Google Drive authentication successful")
    
    def list_videos(self, folder_id: str = None, mime_type: str = 'video/*') -> List[dict]:
        """List all video files in Google Drive folder"""
        if not self.service:
            raise Exception("Google Drive not authenticated")
        
        query = f"mimeType contains 'video/' and trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            pageSize=1000,
            fields="files(id, name, size, mimeType, createdTime)"
        ).execute()
        
        videos = results.get('files', [])
        logger.info(f"Found {len(videos)} videos in Google Drive")
        return videos
    
    def download_video(self, file_id: str, output_path: str):
        """Download video from Google Drive"""
        if not self.service:
            raise Exception("Google Drive not authenticated")
        
        logger.info(f"Downloading video {file_id}...")
        request = self.service.files().get_media(fileId=file_id)
        
        # Download in chunks for large files
        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"Download progress: {progress}%")
        fh.close()
        
        logger.info(f"Downloaded video to {output_path}")
    
    def download_folder(self, folder_id: str, output_dir: str = 'downloaded_videos'):
        """Download all videos from a Google Drive folder"""
        videos = self.list_videos(folder_id)
        os.makedirs(output_dir, exist_ok=True)
        
        for video in videos:
            output_path = os.path.join(output_dir, video['name'])
            try:
                self.download_video(video['id'], output_path)
            except Exception as e:
                logger.error(f"Failed to download {video['name']}: {e}")
        
        return output_dir


class VideoUploadManager:
    """Main manager for uploading videos to multiple platforms"""
    
    def __init__(
        self,
        youtube_uploader: Optional[YouTubeUploader] = None,
        instagram_uploader: Optional[InstagramUploader] = None,
        config_file: str = 'upload_config.json',
        metadata_file: Optional[str] = None
    ):
        self.youtube_uploader = youtube_uploader
        self.instagram_uploader = instagram_uploader
        self.config_file = config_file
        self.config = self.load_config()
        self.upload_history = []
        
        # Initialize metadata handler
        if MetadataHandler:
            self.metadata_handler = MetadataHandler(metadata_file)
        else:
            self.metadata_handler = None
    
    def load_config(self) -> dict:
        """Load upload configuration"""
        default_config = {
            "youtube": {
                "privacy_status": "public",
                "category_id": "22",
                "default_description": "Uploaded via automation",
                "default_tags": []
            },
            "instagram": {
                "default_caption": "Uploaded via automation"
            },
            "upload_delay": 5,  # seconds between uploads
            "retry_attempts": 3
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def process_video(
        self,
        video_path: str,
        title: str = None,
        description: str = None,
        caption: str = None
    ) -> dict:
        """
        Upload a single video to all configured platforms
        
        Args:
            video_path: Path to video file
            title: Override title (if None, uses metadata or filename)
            description: Override description (if None, uses metadata or default)
            caption: Override Instagram caption (if None, uses metadata or default)
        
        Returns dict with upload results
        """
        # Get metadata from handler if available
        if self.metadata_handler:
            metadata = self.metadata_handler.get_metadata(video_path, self.config)
            # Use provided overrides or fall back to metadata
            final_title = title or metadata['title']
            final_description = description or metadata['description']
            final_caption = caption or metadata['instagram_caption']
            youtube_tags = metadata['youtube_tags']
            privacy_status = metadata['privacy_status']
            category_id = metadata['youtube_category']
        else:
            # Fallback to old behavior
            video_name = Path(video_path).stem
            final_title = title or video_name
            final_description = description or self.config['youtube']['default_description']
            final_caption = caption or self.config['instagram']['default_caption']
            youtube_tags = self.config['youtube']['default_tags']
            privacy_status = self.config['youtube']['privacy_status']
            category_id = self.config['youtube']['category_id']
        
        results = {
            'video_path': video_path,
            'title': final_title,
            'timestamp': datetime.now().isoformat(),
            'youtube': None,
            'instagram': None,
            'success': False
        }
        
        # Upload to YouTube
        if self.youtube_uploader:
            youtube_result = self.youtube_uploader.upload_video(
                video_path=video_path,
                title=final_title,
                description=final_description,
                tags=youtube_tags,
                privacy_status=privacy_status,
                category_id=category_id
            )
            results['youtube'] = youtube_result
        
        # Upload to Instagram
        if self.instagram_uploader:
            instagram_result = self.instagram_uploader.upload_video(
                video_path=video_path,
                caption=final_caption
            )
            results['instagram'] = instagram_result
        
        results['success'] = (
            (not self.youtube_uploader or results['youtube']) and
            (not self.instagram_uploader or results['instagram'] or results['instagram'] == "uploaded_with_validation_error")
        )
        
        self.upload_history.append(results)
        return results
    
    def process_directory(
        self,
        directory_path: str,
        video_extensions: List[str] = None
    ):
        """
        Process all videos in a directory
        
        Args:
            directory_path: Path to directory containing videos
            video_extensions: List of video file extensions (default: .mp4, .mov, .avi, .mkv)
        """
        if video_extensions is None:
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        video_files = [
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]
        
        logger.info(f"Found {len(video_files)} videos to upload")
        
        for i, video_file in enumerate(video_files, 1):
            logger.info(f"Processing video {i}/{len(video_files)}: {video_file.name}")
            
            try:
                self.process_video(str(video_file))
                
                # Delay between uploads to avoid rate limiting
                if i < len(video_files):
                    delay = self.config.get('upload_delay', 5)
                    logger.info(f"Waiting {delay} seconds before next upload...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error processing {video_file.name}: {e}")
                continue
        
        self.save_history()
        logger.info(f"Completed processing {len(video_files)} videos")
    
    def save_history(self, history_file: str = 'upload_history.json'):
        """Save upload history to file"""
        with open(history_file, 'w') as f:
            json.dump(self.upload_history, f, indent=2)
        logger.info(f"Upload history saved to {history_file}")


def main():
    """Main function - example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload videos to YouTube and Instagram')
    parser.add_argument('--directory', '-d', type=str, help='Directory containing videos (default: assets folder)')
    parser.add_argument('--video', '-v', type=str, help='Single video file to upload')
    parser.add_argument('--youtube-only', action='store_true', help='Upload only to YouTube')
    parser.add_argument('--instagram-only', action='store_true', help='Upload only to Instagram')
    parser.add_argument('--config', type=str, default='upload_config.json', help='Config file path')
    
    args = parser.parse_args()
    
    # Default to assets folder if no directory specified
    if not args.directory and not args.video:
        project_dir = Path(__file__).parent
        default_assets_folder = project_dir / 'assets'
        if default_assets_folder.exists():
            args.directory = str(default_assets_folder)
            logger.info(f"Using default assets folder: {default_assets_folder}")
    
    # Initialize uploaders
    youtube_uploader = None
    instagram_uploader = None
    
    if not args.instagram_only:
        try:
            youtube_uploader = YouTubeUploader()
        except Exception as e:
            logger.error(f"Failed to initialize YouTube uploader: {e}")
    
    if not args.youtube_only:
        try:
            from upload_config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
            instagram_uploader = InstagramUploader(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        except Exception as e:
            logger.error(f"Failed to initialize Instagram uploader: {e}")
            logger.info("Note: Instagram credentials should be in upload_config.py")
    
    # Initialize manager
    manager = VideoUploadManager(youtube_uploader, instagram_uploader, args.config)
    
    # Process videos
    if args.video:
        manager.process_video(args.video)
    elif args.directory:
        manager.process_directory(args.directory)
    else:
        logger.error("Please provide either --directory or --video argument")
        logger.info("Tip: Create an 'assets' folder and place videos there for automatic detection")
        parser.print_help()


if __name__ == '__main__':
    main()

