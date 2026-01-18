"""Dependency injection factory functions."""

from iphone_backup.backup import iPhonePhotoBackup
from iphone_backup.config import Config


def create_backup_manager(config: Config, backup_dir: str | None = None) -> iPhonePhotoBackup:
    """Create a backup manager instance.

    Args:
        config: Application configuration
        backup_dir: Optional backup directory (overrides config)

    Returns:
        iPhonePhotoBackup instance
    """
    return iPhonePhotoBackup(
        backup_dir=backup_dir if backup_dir else config.get_backup_directory(),
        config_file=config.config_file,
    )
