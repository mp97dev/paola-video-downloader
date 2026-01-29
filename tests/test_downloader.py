"""Unit tests for the VideoDownloader core functionality."""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from downloader import VideoDownloader
from downloader.exceptions import UnsupportedPlatformError, DuplicateFileError
from downloader.providers import BaseProvider


class MockProvider(BaseProvider):
    """Mock provider for testing."""
    
    def __init__(self, name='mock', supported_urls=None):
        self._name = name
        self.supported_urls = supported_urls or []
    
    @property
    def name(self):
        return self._name
    
    def supports(self, url):
        return any(pattern in url for pattern in self.supported_urls)
    
    def extract_info(self, url):
        return {
            'title': 'Test Video',
            'url': url,
            'ext': 'mp4'
        }
    
    def download(self, url, output_path, title=None):
        # Simulate download by creating a file
        filename = f"{title or 'video'}.mp4"
        filepath = os.path.join(output_path, filename)
        with open(filepath, 'w') as f:
            f.write('mock video content')
        return filepath


class TestVideoDownloader(unittest.TestCase):
    """Test VideoDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = 'test_output'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test downloader initialization."""
        mock_provider = MockProvider(supported_urls=['example.com'])
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[mock_provider]
        )
        
        self.assertEqual(downloader.output_dir, self.temp_dir)
        self.assertEqual(len(downloader.providers), 1)
    
    def test_select_provider_success(self):
        """Test selecting a provider that supports the URL."""
        mock_provider = MockProvider(name='mock1', supported_urls=['example.com'])
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[mock_provider]
        )
        
        provider = downloader._select_provider('https://example.com/video')
        self.assertEqual(provider.name, 'mock1')
    
    def test_select_provider_unsupported(self):
        """Test selecting a provider with unsupported URL."""
        mock_provider = MockProvider(supported_urls=['example.com'])
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[mock_provider]
        )
        
        with self.assertRaises(UnsupportedPlatformError):
            downloader._select_provider('https://unsupported.com/video')
    
    def test_download_success(self):
        """Test successful video download."""
        mock_provider = MockProvider(supported_urls=['example.com'])
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[mock_provider]
        )
        
        result = downloader.download('https://example.com/video', 'test_video')
        
        self.assertTrue(result['success'])
        self.assertIn('filepath', result)
        self.assertTrue(os.path.exists(result['filepath']))
    
    def test_download_unsupported_url(self):
        """Test download with unsupported URL."""
        mock_provider = MockProvider(supported_urls=['example.com'])
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[mock_provider]
        )
        
        result = downloader.download('https://unsupported.com/video', 'test_video')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_list_providers(self):
        """Test listing providers."""
        provider1 = MockProvider(name='provider1')
        provider2 = MockProvider(name='provider2')
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[provider1, provider2]
        )
        
        providers = downloader.list_providers()
        self.assertEqual(providers, ['provider1', 'provider2'])
    
    def test_add_provider(self):
        """Test adding a new provider."""
        provider1 = MockProvider(name='provider1')
        provider2 = MockProvider(name='provider2')
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[provider1]
        )
        
        self.assertEqual(len(downloader.providers), 1)
        downloader.add_provider(provider2)
        self.assertEqual(len(downloader.providers), 2)
    
    def test_extract_info(self):
        """Test extracting video info."""
        mock_provider = MockProvider(supported_urls=['example.com'])
        downloader = VideoDownloader(
            output_dir=self.temp_dir,
            providers=[mock_provider]
        )
        
        info = downloader.extract_info('https://example.com/video')
        
        self.assertIsInstance(info, dict)
        self.assertIn('title', info)
        self.assertIn('url', info)


if __name__ == '__main__':
    unittest.main()
