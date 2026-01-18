"""Tests for backup command."""

import unittest
from unittest.mock import Mock, patch

from iphone_backup.commands.backup import backup_photos


class TestBackupCommand(unittest.TestCase):
    """Test cases for backup command."""

    @patch("iphone_backup.commands.backup.iPhonePhotoBackup")
    def test_backup_photos_success(self, mock_backup_class: Mock) -> None:
        """Test successful backup execution."""
        # Setup mock
        mock_backup = Mock()
        mock_backup.backup_all_photos.return_value = True
        mock_backup_class.return_value = mock_backup

        # Execute
        backup_dir = "/tmp/test_backup"
        config_file = "config.yaml"
        backup_photos(backup_dir, config_file)

        # Verify
        mock_backup_class.assert_called_once_with(backup_dir, config_file)
        mock_backup.backup_all_photos.assert_called_once()

    @patch("iphone_backup.commands.backup.iPhonePhotoBackup")
    def test_backup_photos_failure(self, mock_backup_class: Mock) -> None:
        """Test backup failure handling."""
        # Setup mock
        mock_backup = Mock()
        mock_backup.backup_all_photos.return_value = False
        mock_backup_class.return_value = mock_backup

        # Execute and verify exception is raised
        backup_dir = "/tmp/test_backup"
        config_file = "config.yaml"

        with self.assertRaises(RuntimeError):
            backup_photos(backup_dir, config_file)

        mock_backup.backup_all_photos.assert_called_once()


if __name__ == "__main__":
    unittest.main()
