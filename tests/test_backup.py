"""Tests for backup functionality"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from iphone_backup.backup import iPhonePhotoBackup


class TestiPhonePhotoBackup(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.backup = iPhonePhotoBackup(self.temp_dir)
        
        # Mock the dependencies
        self.backup.device = Mock()
        self.backup.scanner = Mock()
        self.backup.date_extractor = Mock()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_backup_directory_creation(self):
        """Test that backup directory is created"""
        backup_dir = Path(self.temp_dir) / "test_backup"
        backup = iPhonePhotoBackup(str(backup_dir))
        
        self.assertTrue(backup_dir.exists())
        self.assertTrue(backup_dir.is_dir())
    
    def test_organize_file_path(self):
        """Test file path organization"""
        file_path = "/DCIM/100APPLE/IMG_001.jpg"
        file_date = datetime(2023, 12, 25, 15, 30, 45)
        
        result = self.backup.organize_file_path(file_path, file_date)
        
        expected = Path(self.temp_dir) / "2023" / "2023-12-25" / "IMG_001.jpg"
        self.assertEqual(result, expected)
    
    def test_organize_file_path_different_dates(self):
        """Test file path organization with different dates"""
        test_cases = [
            (datetime(2023, 1, 1), "2023/2023-01-01/IMG_001.jpg"),
            (datetime(2023, 12, 31), "2023/2023-12-31/IMG_001.jpg"),
            (datetime(2024, 6, 15), "2024/2024-06-15/IMG_001.jpg"),
        ]
        
        for date, expected_path in test_cases:
            with self.subTest(date=date):
                result = self.backup.organize_file_path("/DCIM/IMG_001.jpg", date)
                expected = Path(self.temp_dir) / expected_path
                self.assertEqual(result, expected)
    
    def test_backup_photo_new_file(self):
        """Test backing up a new photo file"""
        photo_path = "/DCIM/100APPLE/IMG_001.jpg"
        file_date = datetime(2023, 12, 25, 15, 30, 45)
        file_data = b"fake_image_data"
        
        # Mock dependencies
        self.backup.date_extractor.get_file_date.return_value = file_date
        self.backup.device.get_file_contents.return_value = file_data
        
        result = self.backup.backup_photo(photo_path)
        
        self.assertTrue(result)
        self.assertEqual(self.backup.stats['backed_up'], 1)
        self.assertEqual(self.backup.stats['skipped'], 0)
        
        # Check file was created
        expected_path = Path(self.temp_dir) / "2023" / "2023-12-25" / "IMG_001.jpg"
        self.assertTrue(expected_path.exists())
        
        # Check file content
        with open(expected_path, 'rb') as f:
            self.assertEqual(f.read(), file_data)
    
    def test_backup_photo_existing_file(self):
        """Test backing up a file that already exists"""
        photo_path = "/DCIM/100APPLE/IMG_001.jpg"
        file_date = datetime(2023, 12, 25, 15, 30, 45)
        
        # Create existing file
        target_dir = Path(self.temp_dir) / "2023" / "2023-12-25"
        target_dir.mkdir(parents=True, exist_ok=True)
        existing_file = target_dir / "IMG_001.jpg"
        existing_file.write_text("existing content")
        
        # Mock dependencies
        self.backup.date_extractor.get_file_date.return_value = file_date
        
        result = self.backup.backup_photo(photo_path)
        
        self.assertTrue(result)
        self.assertEqual(self.backup.stats['backed_up'], 0)
        self.assertEqual(self.backup.stats['skipped'], 1)
        
        # Check file content wasn't changed
        self.assertEqual(existing_file.read_text(), "existing content")
    
    def test_backup_photo_device_error(self):
        """Test handling device errors during backup"""
        photo_path = "/DCIM/100APPLE/IMG_001.jpg"
        file_date = datetime(2023, 12, 25, 15, 30, 45)
        
        # Mock dependencies
        self.backup.date_extractor.get_file_date.return_value = file_date
        self.backup.device.get_file_contents.side_effect = Exception("Device error")
        
        result = self.backup.backup_photo(photo_path)
        
        self.assertFalse(result)
        self.assertEqual(self.backup.stats['backed_up'], 0)
        self.assertEqual(self.backup.stats['errors'], 1)
    
    def test_backup_all_photos_success(self):
        """Test successful backup of all photos"""
        photo_paths = [
            "/DCIM/100APPLE/IMG_001.jpg",
            "/DCIM/100APPLE/IMG_002.jpg",
        ]
        
        # Mock dependencies
        self.backup.device.connect.return_value = True
        self.backup.scanner.scan_for_photos.return_value = photo_paths
        self.backup.date_extractor.get_file_date.return_value = datetime(2023, 12, 25)
        self.backup.device.get_file_contents.return_value = b"fake_data"
        
        result = self.backup.backup_all_photos()
        
        self.assertTrue(result)
        self.assertEqual(self.backup.stats['total_photos'], 2)
        self.assertEqual(self.backup.stats['backed_up'], 2)
    
    def test_backup_all_photos_no_photos(self):
        """Test backup when no photos found"""
        # Mock dependencies
        self.backup.device.connect.return_value = True
        self.backup.scanner.scan_for_photos.return_value = []
        
        result = self.backup.backup_all_photos()
        
        self.assertTrue(result)
        self.assertEqual(self.backup.stats['total_photos'], 0)
    
    def test_backup_all_photos_connection_failed(self):
        """Test backup when device connection fails"""
        self.backup.device.connect.return_value = False
        
        result = self.backup.backup_all_photos()
        
        self.assertFalse(result)
    
    def test_get_backup_stats(self):
        """Test getting backup statistics"""
        # Modify stats
        self.backup.stats['backed_up'] = 5
        self.backup.stats['skipped'] = 3
        self.backup.stats['errors'] = 1
        
        stats = self.backup.get_backup_stats()
        
        expected = {
            'total_photos': 0,
            'backed_up': 5,
            'skipped': 3,
            'errors': 1
        }
        
        self.assertEqual(stats, expected)
        
        # Ensure it returns a copy
        stats['backed_up'] = 999
        self.assertEqual(self.backup.stats['backed_up'], 5)
    
    def test_device_info_connection_success(self):
        """Test device info when connection succeeds"""
        self.backup.device.connect.return_value = True
        
        self.backup.device_info()
        
        self.backup.device.connect.assert_called_once()
        self.backup.device.print_device_info.assert_called_once()
    
    def test_device_info_connection_failed(self):
        """Test device info when connection fails"""
        self.backup.device.connect.return_value = False
        
        self.backup.device_info()
        
        self.backup.device.connect.assert_called_once()
        self.backup.device.print_device_info.assert_not_called()
    
    def test_list_devices(self):
        """Test listing devices"""
        self.backup.list_devices()
        
        self.backup.device.list_devices.assert_called_once()


if __name__ == '__main__':
    unittest.main()