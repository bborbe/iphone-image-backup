"""Device info command implementation."""

import logging

from iphone_backup.backup import iPhonePhotoBackup

logger = logging.getLogger(__name__)


def show_device_info(config_file: str) -> None:
    """Show device information.

    Args:
        config_file: Configuration file path
    """
    logger.info("Fetching device information")

    backup = iPhonePhotoBackup(config_file=config_file)
    backup.device_info()
