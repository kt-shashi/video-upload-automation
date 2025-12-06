"""
Metadata Handler - Manages video titles, descriptions, hashtags, and captions
Supports CSV, JSON, and filename-based metadata extraction
"""

import os
import json
import csv
import re
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class MetadataHandler:
    """Handles video metadata from various sources"""
    
    def __init__(self, metadata_file: Optional[str] = None):
        """
        Initialize metadata handler
        
        Args:
            metadata_file: Path to CSV or JSON file containing video metadata
                          If None, will look for 'video_metadata.csv' or 'video_metadata.json'
        """
        self.metadata_file = metadata_file
        self.metadata = {}
        self.load_metadata()
    
    def load_metadata(self):
        """Load metadata from file (CSV or JSON)"""
        # Try to find metadata file if not specified
        if not self.metadata_file:
            project_dir = Path(__file__).parent
            csv_file = project_dir / 'video_metadata.csv'
            json_file = project_dir / 'video_metadata.json'
            
            if csv_file.exists():
                self.metadata_file = str(csv_file)
            elif json_file.exists():
                self.metadata_file = str(json_file)
        
        if not self.metadata_file or not os.path.exists(self.metadata_file):
            logger.info("No metadata file found. Using filename-based metadata.")
            return
        
        try:
            if self.metadata_file.endswith('.csv'):
                self._load_csv()
            elif self.metadata_file.endswith('.json'):
                self._load_json()
            else:
                logger.warning(f"Unknown metadata file format: {self.metadata_file}")
        except Exception as e:
            logger.error(f"Error loading metadata file: {e}")
    
    def _load_csv(self):
        """Load metadata from CSV file"""
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row.get('filename', '').strip()
                if filename:
                    self.metadata[filename] = {
                        'title': row.get('title', '').strip(),
                        'description': row.get('description', '').strip(),
                        'youtube_tags': self._parse_tags(row.get('youtube_tags', '')),
                        'instagram_caption': row.get('instagram_caption', '').strip(),
                        'instagram_hashtags': self._parse_hashtags(row.get('instagram_hashtags', '')),
                        'youtube_category': row.get('youtube_category', '').strip(),
                        'privacy_status': row.get('privacy_status', '').strip()
                    }
        logger.info(f"Loaded metadata for {len(self.metadata)} videos from CSV")
    
    def _load_json(self):
        """Load metadata from JSON file"""
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    filename = item.get('filename', '').strip()
                    if filename:
                        self.metadata[filename] = item
            elif isinstance(data, dict):
                self.metadata = data
        logger.info(f"Loaded metadata for {len(self.metadata)} videos from JSON")
    
    def _parse_tags(self, tags_str: str) -> List[str]:
        """Parse tags from comma-separated string"""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(',') if tag.strip()]
    
    def _parse_hashtags(self, hashtags_str: str) -> List[str]:
        """Parse hashtags from string (supports #tag format or comma-separated)"""
        if not hashtags_str:
            return []
        
        # Extract hashtags (with or without #)
        hashtags = re.findall(r'#?(\w+)', hashtags_str)
        # Ensure all have # prefix
        return [f'#{tag}' if not tag.startswith('#') else tag for tag in hashtags]
    
    def extract_hashtags_from_text(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    def get_metadata(self, video_path: str, config: Dict) -> Dict:
        """
        Get metadata for a video file
        
        Returns dict with:
        - title: Video title
        - description: YouTube description
        - youtube_tags: List of YouTube tags
        - instagram_caption: Instagram caption
        - instagram_hashtags: List of Instagram hashtags
        - youtube_category: YouTube category ID
        - privacy_status: Privacy status (private/unlisted/public)
        """
        video_file = Path(video_path)
        filename = video_file.name
        filename_stem = video_file.stem
        
        # Try to get metadata from file
        file_metadata = self.metadata.get(filename) or self.metadata.get(filename_stem)
        
        # Extract hashtags from filename if present
        filename_hashtags = self.extract_hashtags_from_text(filename_stem)
        
        # Build metadata
        result = {
            'title': self._get_title(file_metadata, filename_stem),
            'description': self._get_description(file_metadata, config),
            'youtube_tags': self._get_youtube_tags(file_metadata, config, filename_hashtags),
            'instagram_caption': self._get_instagram_caption(file_metadata, config, filename_hashtags, filename_stem),
            'instagram_hashtags': self._get_instagram_hashtags(file_metadata, filename_hashtags, config),
            'youtube_category': self._get_youtube_category(file_metadata, config),
            'privacy_status': self._get_privacy_status(file_metadata, config)
        }
        
        return result
    
    def _get_title(self, file_metadata: Optional[Dict], filename_stem: str) -> str:
        """Get video title"""
        if file_metadata and file_metadata.get('title'):
            return file_metadata['title']
        
        # Clean filename for title (remove hashtags, underscores, etc.)
        title = filename_stem
        # Remove hashtags
        title = re.sub(r'#\w+\s*', '', title)
        # Replace underscores/hyphens with spaces
        title = re.sub(r'[_-]', ' ', title)
        # Capitalize words
        title = ' '.join(word.capitalize() for word in title.split())
        return title
    
    def _get_description(self, file_metadata: Optional[Dict], config: Dict) -> str:
        """Get YouTube description"""
        if file_metadata and file_metadata.get('description'):
            return file_metadata['description']
        return config.get('youtube', {}).get('default_description', 'Uploaded via automation')
    
    def _get_youtube_tags(self, file_metadata: Optional[Dict], config: Dict, filename_hashtags: List[str]) -> List[str]:
        """Get YouTube tags"""
        tags = []
        
        if file_metadata and file_metadata.get('youtube_tags'):
            tags.extend(file_metadata['youtube_tags'])
        
        # Add default tags from config
        default_tags = config.get('youtube', {}).get('default_tags', [])
        tags.extend(default_tags)
        
        # Convert filename hashtags to tags (without #)
        for hashtag in filename_hashtags:
            tag = hashtag.lstrip('#')
            if tag not in tags:
                tags.append(tag)
        
        return list(set(tags))  # Remove duplicates
    
    def _get_instagram_caption(self, file_metadata: Optional[Dict], config: Dict, filename_hashtags: List[str], filename_stem: str = None) -> str:
        """Get Instagram caption"""
        caption_parts = []
        
        if file_metadata and file_metadata.get('instagram_caption'):
            caption_parts.append(file_metadata['instagram_caption'])
        else:
            # Use filename as caption (similar to YouTube title)
            if filename_stem:
                # Clean filename for caption (remove hashtags, underscores, etc.)
                caption = filename_stem
                # Remove hashtags
                caption = re.sub(r'#\w+\s*', '', caption)
                # Replace underscores/hyphens with spaces
                caption = re.sub(r'[_-]', ' ', caption)
                # Capitalize words
                caption = ' '.join(word.capitalize() for word in caption.split())
                caption_parts.append(caption)
            else:
                default_caption = config.get('instagram', {}).get('default_caption', 'Uploaded via automation')
                caption_parts.append(default_caption)
        
        # Add hashtags to caption
        hashtags = self._get_instagram_hashtags(file_metadata, filename_hashtags, config)
        if hashtags:
            caption_parts.append('\n\n' + ' '.join(hashtags))
        
        return '\n'.join(caption_parts)
    
    def _get_instagram_hashtags(self, file_metadata: Optional[Dict], filename_hashtags: List[str], config: Dict) -> List[str]:
        """Get Instagram hashtags"""
        hashtags = []
        
        if file_metadata and file_metadata.get('instagram_hashtags'):
            hashtags.extend(file_metadata['instagram_hashtags'])
        
        # Add hashtags from filename
        hashtags.extend(filename_hashtags)
        
        # Add default hashtags from config
        default_hashtags = config.get('instagram', {}).get('default_hashtags', [])
        hashtags.extend(default_hashtags)
        
        return list(set(hashtags))  # Remove duplicates
    
    def _get_youtube_category(self, file_metadata: Optional[Dict], config: Dict) -> str:
        """Get YouTube category ID"""
        if file_metadata and file_metadata.get('youtube_category'):
            return file_metadata['youtube_category']
        return config.get('youtube', {}).get('category_id', '22')
    
    def _get_privacy_status(self, file_metadata: Optional[Dict], config: Dict) -> str:
        """Get privacy status"""
        if file_metadata and file_metadata.get('privacy_status'):
            return file_metadata['privacy_status']
        return config.get('youtube', {}).get('privacy_status', 'private')


def create_metadata_template_csv(output_file: str = 'video_metadata.csv'):
    """Create a template CSV file for video metadata"""
    template = [
        {
            'filename': 'video1.mp4',
            'title': 'My Amazing Video Title',
            'description': 'This is a detailed description of the video content.\n\nSubscribe for more!',
            'youtube_tags': 'tag1, tag2, tag3',
            'instagram_caption': 'Check out this amazing video! 🎥',
            'instagram_hashtags': '#video #amazing #content',
            'youtube_category': '22',
            'privacy_status': 'private'
        },
        {
            'filename': 'video2.mp4',
            'title': 'Another Great Video',
            'description': 'Description for video 2',
            'youtube_tags': 'tag4, tag5',
            'instagram_caption': 'Another awesome video!',
            'instagram_hashtags': '#awesome #viral',
            'youtube_category': '22',
            'privacy_status': 'unlisted'
        }
    ]
    
    fieldnames = ['filename', 'title', 'description', 'youtube_tags', 'instagram_caption', 
                  'instagram_hashtags', 'youtube_category', 'privacy_status']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(template)
    
    print(f"Created metadata template: {output_file}")
    print("Edit this file to add metadata for your videos.")


def create_metadata_template_json(output_file: str = 'video_metadata.json'):
    """Create a template JSON file for video metadata"""
    template = [
        {
            'filename': 'video1.mp4',
            'title': 'My Amazing Video Title',
            'description': 'This is a detailed description of the video content.\n\nSubscribe for more!',
            'youtube_tags': ['tag1', 'tag2', 'tag3'],
            'instagram_caption': 'Check out this amazing video! 🎥',
            'instagram_hashtags': ['#video', '#amazing', '#content'],
            'youtube_category': '22',
            'privacy_status': 'private'
        },
        {
            'filename': 'video2.mp4',
            'title': 'Another Great Video',
            'description': 'Description for video 2',
            'youtube_tags': ['tag4', 'tag5'],
            'instagram_caption': 'Another awesome video!',
            'instagram_hashtags': ['#awesome', '#viral'],
            'youtube_category': '22',
            'privacy_status': 'unlisted'
        }
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"Created metadata template: {output_file}")
    print("Edit this file to add metadata for your videos.")

