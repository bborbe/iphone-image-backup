"""Tests for fingerprint functionality"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from iphone_backup.fingerprint import FingerprintManager, FileFingerprint


class TestFileFingerprint(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.jpg"
        self.test_file.write_bytes(b"fake_image_data")
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_fingerprint_creation(self):
        """Test creating a fingerprint from a file"""
        fingerprint = FileFingerprint(self.test_file, "abc123", 15)
        
        self.assertEqual(fingerprint.file_path, self.test_file)
        self.assertEqual(fingerprint.content_hash, "abc123")
        self.assertEqual(fingerprint.size, 15)
        self.assertIsNotNone(fingerprint.modified_time)
    
    def test_fingerprint_nonexistent_file(self):
        """Test creating fingerprint for non-existent file"""
        nonexistent = self.temp_dir / "nonexistent.jpg"
        fingerprint = FileFingerprint(nonexistent, "abc123", 15)
        
        self.assertEqual(fingerprint.file_path, nonexistent)
        self.assertEqual(fingerprint.content_hash, "abc123")
        self.assertEqual(fingerprint.size, 15)
        self.assertIsNone(fingerprint.modified_time)


class TestFingerprintManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = FingerprintManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_calculate_content_hash(self):
        """Test SHA-256 hash calculation"""
        test_data = b"test_data"
        expected_hash = "e7d87b738825c33824cf3fd32b7314161fc8c425129163ff5e7260fc7288da36"
        
        result = self.manager.calculate_content_hash(test_data)
        
        self.assertEqual(result, expected_hash)
    
    def test_calculate_content_hash_empty(self):
        """Test hash calculation with empty data"""
        test_data = b""
        expected_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        
        result = self.manager.calculate_content_hash(test_data)
        
        self.assertEqual(result, expected_hash)
    
    def test_build_fingerprint_cache_empty_directory(self):
        """Test building cache with empty directory"""
        self.manager._build_fingerprint_cache()
        
        self.assertEqual(len(self.manager._fingerprint_cache), 0)
        self.assertTrue(self.manager._cache_built)
    
    def test_build_fingerprint_cache_with_files(self):
        """Test building cache with photo files"""
        # Create test files
        (self.temp_dir / "2023").mkdir()
        (self.temp_dir / "2023" / "2023-01-01").mkdir()
        
        test_file1 = self.temp_dir / "2023" / "2023-01-01" / "IMG_001.jpg"
        test_file2 = self.temp_dir / "2023" / "2023-01-01" / "IMG_002.heic"
        test_file3 = self.temp_dir / "2023" / "2023-01-01" / "document.txt"  # Should be ignored
        
        test_file1.write_bytes(b"fake_jpg_data")
        test_file2.write_bytes(b"fake_heic_data")
        test_file3.write_bytes(b"text_data")
        
        self.manager._build_fingerprint_cache()
        
        self.assertEqual(len(self.manager._fingerprint_cache), 2)
        self.assertTrue(self.manager._cache_built)
        
        # Check that only photo files are cached
        cached_files = [fp.file_path.name for fp in self.manager._fingerprint_cache.values()]
        self.assertIn("IMG_001.jpg", cached_files)
        self.assertIn("IMG_002.heic", cached_files)
        self.assertNotIn("document.txt", cached_files)
    
    def test_build_fingerprint_cache_multiple_calls(self):
        """Test that cache is only built once"""
        # Create test file
        test_file = self.temp_dir / "IMG_001.jpg"
        test_file.write_bytes(b"fake_jpg_data")
        
        # First call should build cache
        self.manager._build_fingerprint_cache()
        initial_cache_size = len(self.manager._fingerprint_cache)
        
        # Add another file
        test_file2 = self.temp_dir / "IMG_002.jpg"
        test_file2.write_bytes(b"fake_jpg_data_2")
        
        # Second call should not rebuild cache
        self.manager._build_fingerprint_cache()
        final_cache_size = len(self.manager._fingerprint_cache)
        
        self.assertEqual(initial_cache_size, final_cache_size)
    
    def test_is_duplicate_new_file(self):
        """Test duplicate detection for new file"""
        is_dup, existing = self.manager.is_duplicate(b"new_file_data")
        
        self.assertFalse(is_dup)
        self.assertIsNone(existing)
    
    def test_is_duplicate_existing_file(self):
        """Test duplicate detection for existing file"""
        # Create test file
        test_file = self.temp_dir / "IMG_001.jpg"
        test_data = b"fake_jpg_data"
        test_file.write_bytes(test_data)
        
        # Build cache
        self.manager._build_fingerprint_cache()
        
        # Test duplicate detection
        is_dup, existing = self.manager.is_duplicate(test_data)
        
        self.assertTrue(is_dup)
        self.assertIsNotNone(existing)
        self.assertEqual(existing.file_path, test_file)
        self.assertEqual(existing.size, len(test_data))
    
    def test_get_duplicate_info_new_file(self):
        """Test getting duplicate info for new file"""
        result = self.manager.get_duplicate_info(b"new_file_data")
        
        self.assertEqual(result, {'is_duplicate': False})
    
    def test_get_duplicate_info_existing_file(self):
        """Test getting duplicate info for existing file"""
        # Create test file
        test_file = self.temp_dir / "IMG_001.jpg"
        test_data = b"fake_jpg_data"
        test_file.write_bytes(test_data)
        
        # Build cache
        self.manager._build_fingerprint_cache()
        
        # Test duplicate info
        result = self.manager.get_duplicate_info(test_data)
        
        self.assertTrue(result['is_duplicate'])
        self.assertEqual(result['backup_path'], str(test_file))
        self.assertEqual(result['size'], len(test_data))
        self.assertIsNotNone(result['modified_time'])
    
    def test_add_file_to_cache(self):
        """Test adding file to cache"""
        test_file = self.temp_dir / "IMG_001.jpg"
        test_data = b"fake_jpg_data"
        test_file.write_bytes(test_data)
        
        # Initially empty cache
        self.assertEqual(len(self.manager._fingerprint_cache), 0)
        
        # Add file to cache
        self.manager.add_file_to_cache(test_file, test_data)
        
        # Check cache
        self.assertEqual(len(self.manager._fingerprint_cache), 1)
        
        # Verify fingerprint
        content_hash = self.manager.calculate_content_hash(test_data)
        fingerprint = self.manager._fingerprint_cache[content_hash]
        
        self.assertEqual(fingerprint.file_path, test_file)
        self.assertEqual(fingerprint.size, len(test_data))
        self.assertEqual(fingerprint.content_hash, content_hash)
    
    def test_clear_cache(self):
        """Test clearing the cache"""
        # Create test file and build cache
        test_file = self.temp_dir / "IMG_001.jpg"
        test_file.write_bytes(b"fake_jpg_data")
        self.manager._build_fingerprint_cache()
        
        # Verify cache has content
        self.assertGreater(len(self.manager._fingerprint_cache), 0)
        self.assertTrue(self.manager._cache_built)
        
        # Clear cache
        self.manager.clear_cache()
        
        # Verify cache is empty
        self.assertEqual(len(self.manager._fingerprint_cache), 0)
        self.assertFalse(self.manager._cache_built)
    
    def test_get_stats(self):
        """Test getting statistics"""
        # Create test files
        test_file1 = self.temp_dir / "IMG_001.jpg"
        test_file2 = self.temp_dir / "IMG_002.heic"
        
        test_data1 = b"fake_jpg_data"
        test_data2 = b"fake_heic_data_longer"
        
        test_file1.write_bytes(test_data1)
        test_file2.write_bytes(test_data2)
        
        # Get stats
        stats = self.manager.get_stats()
        
        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(stats['total_size'], len(test_data1) + len(test_data2))
        self.assertEqual(stats['backup_directory'], str(self.temp_dir))
    
    def test_nonexistent_backup_directory(self):
        """Test manager with non-existent backup directory"""
        nonexistent_dir = Path("/nonexistent/path")
        manager = FingerprintManager(nonexistent_dir)
        
        # Should handle gracefully
        manager._build_fingerprint_cache()
        
        self.assertEqual(len(manager._fingerprint_cache), 0)
        self.assertTrue(manager._cache_built)
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted files"""
        # Create test file
        test_file = self.temp_dir / "IMG_001.jpg"
        test_file.write_bytes(b"fake_jpg_data")
        
        # Mock file reading to raise exception
        with patch('builtins.open', side_effect=IOError("File corrupted")):
            self.manager._build_fingerprint_cache()
        
        # Should handle gracefully
        self.assertEqual(len(self.manager._fingerprint_cache), 0)
        self.assertTrue(self.manager._cache_built)
    
    def test_supported_file_extensions(self):
        """Test that only supported extensions are processed"""
        # Create files with various extensions
        supported_files = [
            "IMG_001.jpg", "IMG_002.jpeg", "IMG_003.png", "IMG_004.heic",
            "IMG_005.gif", "IMG_006.tiff", "IMG_007.bmp", "VIDEO_001.mov",
            "VIDEO_002.mp4", "VIDEO_003.m4v", "RAW_001.dng", "RAW_002.raw"
        ]
        
        unsupported_files = [
            "document.txt", "archive.zip", "script.py", "config.yaml"
        ]
        
        # Create all files
        for filename in supported_files + unsupported_files:
            file_path = self.temp_dir / filename
            file_path.write_bytes(f"data_{filename}".encode())
        
        # Build cache
        self.manager._build_fingerprint_cache()
        
        # Should only process supported files
        self.assertEqual(len(self.manager._fingerprint_cache), len(supported_files))
        
        # Check that only supported files are cached
        cached_files = [fp.file_path.name for fp in self.manager._fingerprint_cache.values()]
        for filename in supported_files:
            self.assertIn(filename, cached_files)
        
        for filename in unsupported_files:
            self.assertNotIn(filename, cached_files)


if __name__ == '__main__':
    unittest.main()