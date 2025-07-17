"""File fingerprinting system to prevent duplicate imports"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set, List

logger = logging.getLogger(__name__)


class FileFingerprint:
    """Represents a file's unique fingerprint"""
    
    def __init__(self, file_path: Path, content_hash: str, size: int):
        self.file_path = file_path
        self.content_hash = content_hash
        self.size = size
        self.modified_time = datetime.fromtimestamp(file_path.stat().st_mtime) if file_path.exists() else None


class FingerprintManager:
    """Manages file fingerprinting and deduplication by scanning backup directory"""
    
    def __init__(self, backup_directory: Path):
        self.backup_directory = backup_directory
        self._fingerprint_cache = {}
        self._cache_built = False
    
    def calculate_content_hash(self, file_data: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        try:
            return hashlib.sha256(file_data).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate content hash: {e}")
            return ""
    
    def _build_fingerprint_cache(self):
        """Build cache of fingerprints from backup directory"""
        if self._cache_built:
            return
        
        self._fingerprint_cache = {}
        
        if not self.backup_directory.exists():
            self._cache_built = True
            return
        
        # Scan backup directory for photo files
        photo_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.gif', '.tiff', '.bmp', 
                           '.mov', '.mp4', '.m4v', '.dng', '.raw', '.cr2', '.nef'}
        
        for file_path in self.backup_directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in photo_extensions:
                try:
                    # Calculate hash of existing backup file
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    content_hash = self.calculate_content_hash(file_data)
                    if content_hash:
                        fingerprint = FileFingerprint(file_path, content_hash, len(file_data))
                        self._fingerprint_cache[content_hash] = fingerprint
                        
                except Exception as e:
                    logger.debug(f"Could not fingerprint {file_path}: {e}")
                    continue
        
        self._cache_built = True
        logger.info(f"Built fingerprint cache with {len(self._fingerprint_cache)} files")
    
    def is_duplicate(self, file_data: bytes) -> tuple[bool, Optional[FileFingerprint]]:
        """Check if file is a duplicate based on content hash"""
        # Build cache if not already built
        self._build_fingerprint_cache()
        
        content_hash = self.calculate_content_hash(file_data)
        existing_fingerprint = self._fingerprint_cache.get(content_hash)
        
        if existing_fingerprint:
            return True, existing_fingerprint
        
        return False, None
    
    def get_duplicate_info(self, file_data: bytes) -> Dict:
        """Get information about a duplicate file"""
        is_dup, existing_fingerprint = self.is_duplicate(file_data)
        
        if is_dup and existing_fingerprint:
            return {
                'is_duplicate': True,
                'backup_path': str(existing_fingerprint.file_path),
                'size': existing_fingerprint.size,
                'modified_time': existing_fingerprint.modified_time
            }
        
        return {'is_duplicate': False}
    
    def add_file_to_cache(self, file_path: Path, file_data: bytes):
        """Add a newly backed up file to the cache"""
        content_hash = self.calculate_content_hash(file_data)
        if content_hash:
            fingerprint = FileFingerprint(file_path, content_hash, len(file_data))
            self._fingerprint_cache[content_hash] = fingerprint
    
    def clear_cache(self):
        """Clear the fingerprint cache"""
        self._fingerprint_cache = {}
        self._cache_built = False
    
    def get_stats(self) -> Dict:
        """Get fingerprint statistics"""
        self._build_fingerprint_cache()
        
        total_files = len(self._fingerprint_cache)
        total_size = sum(fp.size for fp in self._fingerprint_cache.values())
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'backup_directory': str(self.backup_directory)
        }