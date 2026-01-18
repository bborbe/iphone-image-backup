"""Backup command implementation."""

import logging

from iphone_backup.backup import iPhonePhotoBackup

logger = logging.getLogger(__name__)


def backup_photos(backup_dir: str | None, config_file: str) -> None:
    """Backup all photos from iPhone.

    Args:
        backup_dir: Backup directory path (None to use config default)
        config_file: Configuration file path
    """
    logger.info("Starting iPhone photo backup")

    print("🍎 iPhone Photo Backup Tool")
    print("=" * 30)

    backup = iPhonePhotoBackup(backup_dir, config_file)
    success = backup.backup_all_photos()

    if success:
        print("\n🎉 Backup completed successfully!")
    else:
        print("\n💥 Backup failed!")
        raise RuntimeError("Backup failed")
