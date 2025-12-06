"""
Quick upload script - simplified interface for uploading videos
"""

import os
import sys
from pathlib import Path
from video_uploader import (
    YouTubeUploader, 
    InstagramUploader, 
    VideoUploadManager,
    GoogleDriveDownloader
)

def setup_uploaders():
    """Initialize uploaders with error handling"""
    youtube_uploader = None
    instagram_uploader = None
    
    # Setup YouTube
    print("Setting up YouTube...")
    try:
        youtube_uploader = YouTubeUploader()
        print("✓ YouTube ready")
    except Exception as e:
        print(f"✗ YouTube setup failed: {e}")
        response = input("Continue without YouTube? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Setup Instagram
    print("\nSetting up Instagram...")
    try:
        from upload_config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
        if INSTAGRAM_USERNAME == "your_instagram_username":
            print("⚠ Instagram credentials not configured in upload_config.py")
            response = input("Skip Instagram setup? (y/n): ")
            if response.lower() == 'y':
                pass
            else:
                username = input("Enter Instagram username: ")
                password = input("Enter Instagram password: ")
                instagram_uploader = InstagramUploader(username, password)
                print("✓ Instagram ready")
        else:
            instagram_uploader = InstagramUploader(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            print("✓ Instagram ready")
    except Exception as e:
        print(f"✗ Instagram setup failed: {e}")
        response = input("Continue without Instagram? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    return youtube_uploader, instagram_uploader


def main():
    print("=" * 60)
    print("Automated Video Uploader - Quick Start")
    print("=" * 60)
    print()
    
    # Default to assets folder in project directory
    project_dir = Path(__file__).parent
    default_assets_folder = project_dir / 'assets'
    
    # Check if directory or file provided
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # Default to assets folder if it exists, otherwise ask user
        if default_assets_folder.exists():
            print(f"No path provided. Using default: {default_assets_folder}")
            path = str(default_assets_folder)
        else:
            path = input(f"Enter video file or directory path (or press Enter to use 'assets' folder): ").strip().strip('"')
            if not path:
                path = str(default_assets_folder)
    
    if not os.path.exists(path):
        print(f"Error: Path not found: {path}")
        if path == str(default_assets_folder):
            print(f"Tip: Create the 'assets' folder and add your videos there!")
        sys.exit(1)
    
    # Check if Google Drive
    use_drive = False
    if 'drive.google.com' in path or path.startswith('drive:'):
        use_drive = True
        print("\nGoogle Drive detected!")
        print("Note: For Google Drive, you need to provide the folder ID")
        folder_id = input("Enter Google Drive folder ID: ").strip()
        
        print("\nSetting up Google Drive...")
        try:
            drive = GoogleDriveDownloader()
            if drive.service:
                print("✓ Google Drive ready")
                download_dir = drive.download_folder(folder_id)
                path = download_dir
                print(f"✓ Videos downloaded to: {download_dir}")
            else:
                print("✗ Google Drive setup failed")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Google Drive error: {e}")
            sys.exit(1)
    
    # Setup uploaders
    youtube_uploader, instagram_uploader = setup_uploaders()
    
    if not youtube_uploader and not instagram_uploader:
        print("\nError: No uploaders configured!")
        sys.exit(1)
    
    # Initialize manager
    manager = VideoUploadManager(youtube_uploader, instagram_uploader)
    
    # Process videos
    print("\n" + "=" * 60)
    print("Starting upload process...")
    print("=" * 60)
    
    if os.path.isfile(path):
        print(f"\nUploading single video: {path}")
        result = manager.process_video(path)
        if result['success']:
            print("\n✓ Upload successful!")
        else:
            print("\n✗ Upload completed with errors. Check upload_log.txt for details.")
    else:
        print(f"\nProcessing directory: {path}")
        manager.process_directory(path)
        print("\n✓ Batch upload completed!")
    
    # Show summary
    print("\n" + "=" * 60)
    print("Upload Summary")
    print("=" * 60)
    successful = sum(1 for r in manager.upload_history if r['success'])
    total = len(manager.upload_history)
    print(f"Total videos processed: {total}")
    print(f"Successful uploads: {successful}")
    print(f"Failed uploads: {total - successful}")
    print(f"\nDetailed history saved to: upload_history.json")
    print(f"Logs saved to: upload_log.txt")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nUpload interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

