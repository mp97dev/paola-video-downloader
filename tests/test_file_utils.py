"""Unit tests for file utility functions."""

import unittest
import os
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from downloader.utils import (
    sanitize_filename,
    ensure_extension,
    check_duplicate,
    get_file_hash
)


class TestFileUtils(unittest.TestCase):
    """Test file utility functions."""
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        # Test removing invalid characters
        result = sanitize_filename('test<>:"/\\|?*file')
        self.assertEqual(result, 'testfile')
    
    def test_sanitize_filename_spaces(self):
        """Test space handling."""
        result = sanitize_filename('test   multiple   spaces')
        self.assertEqual(result, 'test multiple spaces')
    
    def test_sanitize_filename_dots(self):
        """Test leading/trailing dots."""
        result = sanitize_filename('...test...')
        self.assertEqual(result, 'test')
    
    def test_sanitize_filename_length_limit(self):
        """Test length limiting."""
        long_name = 'a' * 300
        result = sanitize_filename(long_name, max_length=50)
        self.assertLessEqual(len(result), 50)
    
    def test_sanitize_filename_empty(self):
        """Test empty filename handling."""
        result = sanitize_filename('')
        self.assertEqual(result, 'video')
    
    def test_ensure_extension_adds(self):
        """Test adding extension."""
        result = ensure_extension('video', '.mp4')
        self.assertEqual(result, 'video.mp4')
    
    def test_ensure_extension_without_dot(self):
        """Test extension without leading dot."""
        result = ensure_extension('video', 'mp4')
        self.assertEqual(result, 'video.mp4')
    
    def test_ensure_extension_already_has(self):
        """Test when extension already exists."""
        result = ensure_extension('video.mp4', '.mp4')
        self.assertEqual(result, 'video.mp4')
    
    def test_ensure_extension_replaces(self):
        """Test replacing wrong extension."""
        result = ensure_extension('video.avi', '.mp4')
        self.assertEqual(result, 'video.mp4')
    
    def test_check_duplicate_exists(self):
        """Test duplicate detection when file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / 'test.mp4'
            test_file.touch()
            
            result = check_duplicate('test.mp4', tmpdir)
            self.assertIsNotNone(result)
            self.assertTrue(result.endswith('test.mp4'))
    
    def test_check_duplicate_not_exists(self):
        """Test duplicate detection when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_duplicate('nonexistent.mp4', tmpdir)
            self.assertIsNone(result)
    
    def test_get_file_hash(self):
        """Test file hash calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test content')
            temp_path = f.name
        
        try:
            hash1 = get_file_hash(temp_path)
            self.assertIsInstance(hash1, str)
            self.assertEqual(len(hash1), 32)  # MD5 hash is 32 chars
            
            # Same file should produce same hash
            hash2 = get_file_hash(temp_path)
            self.assertEqual(hash1, hash2)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
