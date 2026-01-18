"""List devices command implementation."""

import logging

from iphone_backup.backup import iPhonePhotoBackup

logger = logging.getLogger(__name__)


def list_connected_devices(config_file: str) -> None:
    """List all connected iOS devices.

    Args:
        config_file: Configuration file path
    """
    logger.info("Listing connected devices")

    backup = iPhonePhotoBackup(config_file=config_file)
    backup.list_devices()
