"""Main backup functionality"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from .device import iPhoneDevice
from .scanner import PhotoScanner
from .date_extractor import DateExtractor
from .config import BackupConfig
from .fingerprint import FingerprintManager

logger = logging.getLogger(__name__)


class iPhonePhotoBackup:
    """Main backup class that orchestrates the backup process"""
    
    def __init__(self, backup_dir: str = None, config_file: str = None):
        """Initialize iPhone photo backup"""
        self.config = BackupConfig(config_file)
        
        # Use config default if no backup_dir specified
        if not backup_dir:
            backup_dir = self.config.get_backup_directory()
            backup_dir = Path(backup_dir).expanduser()
        
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.device = iPhoneDevice()
        self.scanner = PhotoScanner(self.device, self.config)
        self.date_extractor = DateExtractor(self.device)
        self.fingerprint_manager = FingerprintManager(self.backup_dir)
        
        self.stats = {
            'total_photos': 0,
            'backed_up': 0,
            'skipped': 0,
            'duplicates': 0,
            'errors': 0
        }
    
    def backup_all_photos(self) -> bool:
        """Backup all photos from iPhone"""
        if not self.device.connect():
            return False

        try:
            # Get all photo paths
            photo_paths = self.scanner.scan_for_photos()

            if not photo_paths:
                print("📭 No photos found on device")
                return True

            self.stats['total_photos'] = len(photo_paths)

            print(f"\n🚀 Starting backup of {len(photo_paths)} items...")
            print(f"📁 Backup location: {self.backup_dir}")
            print("-" * 50)

            # Backup each photo
            for i, photo_path in enumerate(photo_paths, 1):
                print(f"[{i}/{len(photo_paths)}] ", end="")
                self.backup_photo(photo_path)

            # Print summary
            self._print_summary()
            return True

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            print(f"❌ Backup failed: {e}")
            return False
    
    def backup_photo(self, photo_path: str) -> bool:
        """Backup a single photo"""
        try:
            # Check if file should be excluded (double-check in case scanner missed it)
            if self.config.should_exclude_file(photo_path):
                print(f"⏭️  Excluding: {Path(photo_path).name} (configured exclusion)")
                self.stats['skipped'] += 1
                return True

            # Get file data first for fingerprinting
            file_data = self.device.get_file_contents(photo_path)
            
            # Check if this is a duplicate based on content hash
            duplicate_info = self.fingerprint_manager.get_duplicate_info(file_data)
            if duplicate_info['is_duplicate']:
                backup_path = duplicate_info.get('backup_path', 'unknown location')
                print(f"⏭️  Skipping duplicate: {Path(photo_path).name} (already backed up as {Path(backup_path).name})")
                self.stats['duplicates'] += 1
                return True

            # Get file date
            file_date = self.date_extractor.get_file_date(photo_path)
            
            # Check if original file already exists by path
            filename = Path(photo_path).name
            year_date = file_date.strftime("%Y/%Y-%m-%d")
            target_dir = self.backup_dir / year_date
            target_dir.mkdir(parents=True, exist_ok=True)
            original_path = target_dir / filename

            # Skip if already exists by path
            if original_path.exists():
                print(f"⏭️  Skipping existing: {filename}")
                self.stats['skipped'] += 1
                return True

            # Download file to original path
            print(f"📥 Downloading: {filename} → {year_date}/")

            with open(original_path, 'wb') as local_file:
                local_file.write(file_data)

            # Add fingerprint to cache
            self.fingerprint_manager.add_file_to_cache(original_path, file_data)

            self.stats['backed_up'] += 1
            return True

        except Exception as e:
            logger.error(f"Failed to backup {photo_path}: {e}")
            print(f"❌ Error backing up {Path(photo_path).name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def list_devices(self):
        """List all connected devices"""
        self.device.list_devices()
    
    def device_info(self):
        """Show device information"""
        if not self.device.connect():
            return
        self.device.print_device_info()
    
    def get_backup_stats(self) -> Dict[str, int]:
        """Get backup statistics"""
        return self.stats.copy()
    
    def _print_summary(self):
        """Print backup summary"""
        print("\n" + "=" * 50)
        print("📊 BACKUP SUMMARY")
        print("=" * 50)
        print(f"📸 Total photos found: {self.stats['total_photos']}")
        print(f"✅ Successfully backed up: {self.stats['backed_up']}")
        print(f"⏭️  Skipped (already exist): {self.stats['skipped']}")
        print(f"🔄 Skipped (duplicates): {self.stats['duplicates']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"📁 Backup location: {self.backup_dir}")
    
    def organize_file_path(self, file_path: str, file_date: datetime) -> Path:
        """Generate organized backup path - used for testing"""
        filename = Path(file_path).name
        year_date = file_date.strftime("%Y/%Y-%m-%d")
        target_dir = self.backup_dir / year_date
        return target_dir / filename