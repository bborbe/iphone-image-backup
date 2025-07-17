"""Date extraction from photos"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from io import BytesIO

from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)


class DateExtractor:
    """Extracts creation dates from photo files"""
    
    def __init__(self, device):
        self.device = device
    
    def get_file_date(self, file_path: str) -> datetime:
        """Get file creation date from EXIF data or filesystem"""
        
        # Try to extract date from EXIF data
        exif_date = self._extract_exif_date(file_path)
        if exif_date:
            return exif_date
        
        # Try to get filesystem date as fallback
        filesystem_date = self._get_filesystem_date(file_path)
        if filesystem_date:
            return filesystem_date
        
        # Last resort: use current date
        logger.warning(f"Could not determine date for {file_path}, using current date")
        return datetime.now()
    
    def _extract_exif_date(self, file_path: str) -> Optional[datetime]:
        """Extract date from EXIF data"""
        try:
            # Get file data
            file_data = self.device.get_file_contents(file_path)
            image = Image.open(BytesIO(file_data))
            
            # Get EXIF data
            exif_data = image._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        try:
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                        except ValueError:
                            continue
                            
        except Exception as e:
            logger.debug(f"Could not extract EXIF date from {file_path}: {e}")
        
        return None
    
    def _get_filesystem_date(self, file_path: str) -> Optional[datetime]:
        """Get date from filesystem metadata"""
        try:
            stat_info = self.device.stat(file_path)
            if hasattr(stat_info, 'st_mtime') and stat_info.st_mtime > 0:
                return datetime.fromtimestamp(stat_info.st_mtime)
            elif hasattr(stat_info, 'st_ctime') and stat_info.st_ctime > 0:
                return datetime.fromtimestamp(stat_info.st_ctime)
        except Exception as e:
            logger.debug(f"Could not get filesystem date for {file_path}: {e}")
        
        return None