"""Photo scanning functionality"""

import logging
from pathlib import Path
from typing import List, Set

logger = logging.getLogger(__name__)


class PhotoScanner:
    """Scans iPhone for photos and videos"""
    
    def __init__(self, device):
        self.device = device
        self.photo_extensions = {
            '.jpg', '.jpeg', '.png', '.heic', '.gif', '.tiff', '.bmp', 
            '.mov', '.mp4', '.m4v', '.dng'
        }
        self.skip_dirs = {
            'Thumbnails', 'thumbnails', 'Cache', 'cache', 'Metadata', 'metadata',
            '.thumbnails', '.cache', 'V2', 'v2'
        }
    
    def scan_for_photos(self) -> List[str]:
        """Get all photo file paths from iPhone"""
        photo_paths = []
        
        try:
            # Focus on actual photo directories
            photo_dirs = ['/DCIM']

            print("📂 Scanning for photos...")

            for base_dir in photo_dirs:
                try:
                    if self.device.exists(base_dir):
                        print(f"   Checking {base_dir}...")
                        for root, dirs, files in self.device.walk(base_dir):
                            # Skip thumbnail and cache directories
                            if self._should_skip_directory(root):
                                continue
                                
                            for file in files:
                                file_path = f"{root}/{file}"
                                file_ext = Path(file).suffix.lower()

                                if file_ext in self.photo_extensions:
                                    photo_paths.append(file_path)

                except Exception as e:
                    logger.warning(f"Could not access {base_dir}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scanning for photos: {e}")

        print(f"📸 Found {len(photo_paths)} photos/videos")
        return photo_paths
    
    def _should_skip_directory(self, directory_path: str) -> bool:
        """Check if directory should be skipped (thumbnails, cache, etc.)"""
        return any(skip_pattern in directory_path for skip_pattern in 
                  ['/Thumbnails/', '/Cache/', '/Metadata/'])
    
    def is_photo_file(self, file_path: str) -> bool:
        """Check if file is a supported photo/video format"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.photo_extensions