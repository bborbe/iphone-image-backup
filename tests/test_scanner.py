"""Tests for photo scanner functionality"""

import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from iphone_backup.scanner import PhotoScanner


class TestPhotoScanner(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_device = Mock()
        self.scanner = PhotoScanner(self.mock_device)
    
    def test_is_photo_file_supported_formats(self):
        """Test photo file detection for supported formats"""
        test_cases = [
            ('IMG_001.jpg', True),
            ('IMG_002.HEIC', True),
            ('IMG_003.png', True),
            ('IMG_004.mov', True),
            ('IMG_005.mp4', True),
            ('IMG_006.dng', True),
            ('document.txt', False),
            ('readme.md', False),
            ('config.yaml', False),
            ('script.py', False),
            ('IMG_007.JPG', True),  # Test case sensitivity
            ('IMG_008.PNG', True),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.scanner.is_photo_file(filename)
                self.assertEqual(result, expected, 
                               f"Expected {expected} for {filename}, got {result}")
    
    def test_should_skip_directory(self):
        """Test directory skipping logic"""
        test_cases = [
            ('/DCIM/100APPLE', False),
            ('/DCIM/Thumbnails/100APPLE', True),
            ('/DCIM/Cache/data', True),
            ('/DCIM/Metadata/info', True),
            ('/DCIM/119APPLE', False),
            ('/PhotoData/Thumbnails/V2', True),
            ('/PhotoData/Cache/temp', True),
            ('/Media/DCIM/regular', False),
        ]
        
        for directory, expected in test_cases:
            with self.subTest(directory=directory):
                result = self.scanner._should_skip_directory(directory)
                self.assertEqual(result, expected,
                               f"Expected {expected} for {directory}, got {result}")
    
    def test_scan_for_photos_empty_directory(self):
        """Test scanning when no photos found"""
        self.mock_device.exists.return_value = True
        self.mock_device.walk.return_value = [
            ('/DCIM', [], ['readme.txt', 'config.bin']),
            ('/DCIM/100APPLE', [], ['document.pdf', 'notes.txt']),
        ]
        
        result = self.scanner.scan_for_photos()
        
        self.assertEqual(result, [])
        self.mock_device.exists.assert_called_with('/DCIM')
    
    def test_scan_for_photos_with_photos(self):
        """Test scanning with actual photos"""
        self.mock_device.exists.return_value = True
        self.mock_device.walk.return_value = [
            ('/DCIM', [], ['readme.txt']),
            ('/DCIM/100APPLE', [], ['IMG_001.jpg', 'IMG_002.HEIC', 'config.bin']),
            ('/DCIM/101APPLE', [], ['IMG_003.png', 'IMG_004.mov']),
        ]
        
        result = self.scanner.scan_for_photos()
        
        expected = [
            '/DCIM/100APPLE/IMG_001.jpg',
            '/DCIM/100APPLE/IMG_002.HEIC',
            '/DCIM/101APPLE/IMG_003.png',
            '/DCIM/101APPLE/IMG_004.mov'
        ]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_scan_for_photos_skips_thumbnail_directories(self):
        """Test that thumbnail directories are skipped"""
        self.mock_device.exists.return_value = True
        self.mock_device.walk.return_value = [
            ('/DCIM', [], []),
            ('/DCIM/100APPLE', [], ['IMG_001.jpg']),
            ('/DCIM/Thumbnails/100APPLE', [], ['thumb_001.jpg']),
            ('/DCIM/Cache/data', [], ['cache_001.jpg']),
            ('/DCIM/101APPLE', [], ['IMG_002.HEIC']),
        ]
        
        result = self.scanner.scan_for_photos()
        
        expected = [
            '/DCIM/100APPLE/IMG_001.jpg',
            '/DCIM/101APPLE/IMG_002.HEIC'
        ]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_scan_for_photos_device_not_accessible(self):
        """Test handling when device directory is not accessible"""
        self.mock_device.exists.return_value = False
        
        result = self.scanner.scan_for_photos()
        
        self.assertEqual(result, [])
        self.mock_device.exists.assert_called_with('/DCIM')
    
    def test_scan_for_photos_walk_exception(self):
        """Test handling of walk exceptions"""
        self.mock_device.exists.return_value = True
        self.mock_device.walk.side_effect = Exception("Device access error")
        
        result = self.scanner.scan_for_photos()
        
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()