"""Tests for info command."""

import unittest
from unittest.mock import Mock, patch

from iphone_backup.commands.info import show_device_info


class TestInfoCommand(unittest.TestCase):
    """Test cases for info command."""

    @patch("iphone_backup.commands.info.iPhonePhotoBackup")
    def test_show_device_info(self, mock_backup_class: Mock) -> None:
        """Test device info execution."""
        # Setup mock
        mock_backup = Mock()
        mock_backup_class.return_value = mock_backup

        # Execute
        config_file = "config.yaml"
        show_device_info(config_file)

        # Verify
        mock_backup_class.assert_called_once_with(config_file=config_file)
        mock_backup.device_info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
