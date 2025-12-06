"""
Google Drive Helper - List and download videos from Google Drive
"""

import os
import sys
from video_uploader import GoogleDriveDownloader

def list_drive_videos(folder_id: str = None):
    """List all videos in Google Drive"""
    print("Connecting to Google Drive...")
    drive = GoogleDriveDownloader()
    
    if not drive.service:
        print("Error: Google Drive not authenticated")
        print("Make sure you have drive_credentials.json in the project directory")
        return
    
    print("\nFetching videos...")
    videos = drive.list_videos(folder_id)
    
    if not videos:
        print("No videos found.")
        return
    
    print(f"\nFound {len(videos)} videos:\n")
    print("-" * 80)
    print(f"{'Name':<50} {'Size':<15} {'ID':<30}")
    print("-" * 80)
    
    for video in videos:
        size = video.get('size', 'Unknown')
        if size != 'Unknown':
            size_mb = int(size) / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = "Unknown"
        
        name = video['name'][:47] + "..." if len(video['name']) > 50 else video['name']
        print(f"{name:<50} {size_str:<15} {video['id']:<30}")
    
    print("-" * 80)
    
    # Save to file
    import json
    with open('drive_videos.json', 'w') as f:
        json.dump(videos, f, indent=2)
    
    print(f"\nVideo list saved to: drive_videos.json")
    
    return videos


def download_from_drive(folder_id: str = None, output_dir: str = 'downloaded_videos'):
    """Download all videos from Google Drive folder"""
    print("Connecting to Google Drive...")
    drive = GoogleDriveDownloader()
    
    if not drive.service:
        print("Error: Google Drive not authenticated")
        return
    
    print(f"\nDownloading videos to: {output_dir}")
    drive.download_folder(folder_id, output_dir)
    print(f"\n✓ Download complete! Videos saved to: {output_dir}")


def main():
    print("=" * 60)
    print("Google Drive Video Helper")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python drive_helper.py list [folder_id]")
        print("  python drive_helper.py download [folder_id] [output_dir]")
        print()
        print("Examples:")
        print("  python drive_helper.py list")
        print("  python drive_helper.py list 1a2b3c4d5e6f7g8h9i0j")
        print("  python drive_helper.py download 1a2b3c4d5e6f7g8h9i0j")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        folder_id = sys.argv[2] if len(sys.argv) > 2 else None
        list_drive_videos(folder_id)
    
    elif command == 'download':
        if len(sys.argv) < 3:
            print("Error: Folder ID required for download")
            sys.exit(1)
        
        folder_id = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else 'downloaded_videos'
        download_from_drive(folder_id, output_dir)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()

