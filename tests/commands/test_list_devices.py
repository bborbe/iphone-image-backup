"""Tests for list-devices command."""

import unittest
from unittest.mock import Mock, patch

from iphone_backup.commands.list_devices import list_connected_devices


class TestListDevicesCommand(unittest.TestCase):
    """Test cases for list-devices command."""

    @patch("iphone_backup.commands.list_devices.iPhonePhotoBackup")
    def test_list_connected_devices(self, mock_backup_class: Mock) -> None:
        """Test list devices execution."""
        # Setup mock
        mock_backup = Mock()
        mock_backup_class.return_value = mock_backup

        # Execute
        config_file = "config.yaml"
        list_connected_devices(config_file)

        # Verify
        mock_backup_class.assert_called_once_with(config_file=config_file)
        mock_backup.list_devices.assert_called_once()


if __name__ == "__main__":
    unittest.main()
