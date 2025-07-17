"""Tests for date extraction functionality"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from iphone_backup.date_extractor import DateExtractor


class TestDateExtractor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_device = Mock()
        self.extractor = DateExtractor(self.mock_device)
    
    @patch('iphone_backup.date_extractor.Image')
    def test_extract_exif_date_success(self, mock_image):
        """Test successful EXIF date extraction"""
        # Mock EXIF data
        mock_img = Mock()
        mock_img._getexif.return_value = {
            306: '2023:12:25 15:30:45',  # DateTime tag
            36867: '2023:12:25 15:30:45',  # DateTimeOriginal tag
        }
        mock_image.open.return_value = mock_img
        
        # Mock device file contents
        self.mock_device.get_file_contents.return_value = b'fake_image_data'
        
        result = self.extractor._extract_exif_date('/DCIM/IMG_001.jpg')
        
        expected = datetime(2023, 12, 25, 15, 30, 45)
        self.assertEqual(result, expected)
    
    @patch('iphone_backup.date_extractor.Image')
    def test_extract_exif_date_no_exif(self, mock_image):
        """Test EXIF extraction when no EXIF data available"""
        mock_img = Mock()
        mock_img._getexif.return_value = None
        mock_image.open.return_value = mock_img
        
        self.mock_device.get_file_contents.return_value = b'fake_image_data'
        
        result = self.extractor._extract_exif_date('/DCIM/IMG_001.jpg')
        
        self.assertIsNone(result)
    
    @patch('iphone_backup.date_extractor.Image')
    def test_extract_exif_date_invalid_format(self, mock_image):
        """Test EXIF extraction with invalid date format"""
        mock_img = Mock()
        mock_img._getexif.return_value = {
            306: 'invalid_date_format',  # Invalid format
        }
        mock_image.open.return_value = mock_img
        
        self.mock_device.get_file_contents.return_value = b'fake_image_data'
        
        result = self.extractor._extract_exif_date('/DCIM/IMG_001.jpg')
        
        self.assertIsNone(result)
    
    @patch('iphone_backup.date_extractor.Image')
    def test_extract_exif_date_exception(self, mock_image):
        """Test EXIF extraction when exception occurs"""
        mock_image.open.side_effect = Exception("Image processing error")
        
        self.mock_device.get_file_contents.return_value = b'fake_image_data'
        
        result = self.extractor._extract_exif_date('/DCIM/IMG_001.jpg')
        
        self.assertIsNone(result)
    
    def test_get_filesystem_date_success(self):
        """Test successful filesystem date extraction"""
        mock_stat = Mock()
        mock_stat.st_mtime = 1703518245.0  # Unix timestamp for 2023-12-25 15:30:45
        
        self.mock_device.stat.return_value = mock_stat
        
        result = self.extractor._get_filesystem_date('/DCIM/IMG_001.jpg')
        
        expected = datetime.fromtimestamp(1703518245.0)
        self.assertEqual(result, expected)
    
    def test_get_filesystem_date_ctime_fallback(self):
        """Test filesystem date extraction using ctime fallback"""
        mock_stat = Mock()
        mock_stat.st_mtime = 0  # Invalid mtime
        mock_stat.st_ctime = 1703518245.0  # Use ctime instead
        
        self.mock_device.stat.return_value = mock_stat
        
        result = self.extractor._get_filesystem_date('/DCIM/IMG_001.jpg')
        
        expected = datetime.fromtimestamp(1703518245.0)
        self.assertEqual(result, expected)
    
    def test_get_filesystem_date_no_valid_timestamps(self):
        """Test filesystem date extraction with no valid timestamps"""
        mock_stat = Mock()
        mock_stat.st_mtime = 0
        mock_stat.st_ctime = 0
        
        self.mock_device.stat.return_value = mock_stat
        
        result = self.extractor._get_filesystem_date('/DCIM/IMG_001.jpg')
        
        self.assertIsNone(result)
    
    def test_get_filesystem_date_exception(self):
        """Test filesystem date extraction when exception occurs"""
        self.mock_device.stat.side_effect = Exception("Stat error")
        
        result = self.extractor._get_filesystem_date('/DCIM/IMG_001.jpg')
        
        self.assertIsNone(result)
    
    @patch('iphone_backup.date_extractor.datetime')
    def test_get_file_date_exif_success(self, mock_datetime):
        """Test get_file_date with successful EXIF extraction"""
        expected_date = datetime(2023, 12, 25, 15, 30, 45)
        mock_datetime.now.return_value = datetime(2023, 12, 26, 10, 0, 0)
        
        with patch.object(self.extractor, '_extract_exif_date', return_value=expected_date):
            result = self.extractor.get_file_date('/DCIM/IMG_001.jpg')
            
            self.assertEqual(result, expected_date)
    
    @patch('iphone_backup.date_extractor.datetime')
    def test_get_file_date_filesystem_fallback(self, mock_datetime):
        """Test get_file_date falling back to filesystem date"""
        filesystem_date = datetime(2023, 12, 25, 10, 0, 0)
        current_date = datetime(2023, 12, 26, 10, 0, 0)
        mock_datetime.now.return_value = current_date
        
        with patch.object(self.extractor, '_extract_exif_date', return_value=None):
            with patch.object(self.extractor, '_get_filesystem_date', return_value=filesystem_date):
                result = self.extractor.get_file_date('/DCIM/IMG_001.jpg')
                
                self.assertEqual(result, filesystem_date)
    
    @patch('iphone_backup.date_extractor.datetime')
    def test_get_file_date_current_date_fallback(self, mock_datetime):
        """Test get_file_date falling back to current date"""
        current_date = datetime(2023, 12, 26, 10, 0, 0)
        mock_datetime.now.return_value = current_date
        
        with patch.object(self.extractor, '_extract_exif_date', return_value=None):
            with patch.object(self.extractor, '_get_filesystem_date', return_value=None):
                result = self.extractor.get_file_date('/DCIM/IMG_001.jpg')
                
                self.assertEqual(result, current_date)


if __name__ == '__main__':
    unittest.main()