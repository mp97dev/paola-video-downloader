"""
Example Usage of the Enhanced Video Downloader

This script demonstrates how to use the modular video downloader
with various platforms and configurations.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from downloader import VideoDownloader
from downloader.exceptions import DownloadError, UnsupportedPlatformError


def example_basic_download():
    """Example: Basic video download."""
    print("\n=== Example 1: Basic Download ===")
    
    # Initialize the downloader
    downloader = VideoDownloader(output_dir='./downloads')
    
    # Download a video
    url = 'https://www.instagram.com/p/example/'
    title = 'my_video'
    
    try:
        result = downloader.download(url, title)
        
        if result['success']:
            print(f"✓ Downloaded successfully: {result['filepath']}")
            print(f"  Provider used: {result['provider']}")
        else:
            print(f"✗ Download failed: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_extract_info():
    """Example: Extract video information without downloading."""
    print("\n=== Example 2: Extract Video Info ===")
    
    downloader = VideoDownloader()
    url = 'https://www.youtube.com/watch?v=example'
    
    try:
        info = downloader.extract_info(url)
        print(f"Title: {info.get('title')}")
        print(f"Duration: {info.get('duration')} seconds")
        print(f"Uploader: {info.get('uploader')}")
        print(f"Extension: {info.get('ext')}")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_duplicate_prevention():
    """Example: Prevent duplicate downloads."""
    print("\n=== Example 3: Duplicate Prevention ===")
    
    # Enable duplicate prevention
    downloader = VideoDownloader(
        output_dir='./downloads',
        prevent_duplicates=True
    )
    
    url = 'https://www.instagram.com/p/example/'
    title = 'existing_video'
    
    try:
        result = downloader.download(url, title)
        print(f"First download: {result['success']}")
        
        # Try downloading again - should be prevented
        result2 = downloader.download(url, title)
        print(f"Second download: {result2['success']}")
    except Exception as e:
        print(f"Duplicate prevented: {e}")


def example_list_providers():
    """Example: List available providers."""
    print("\n=== Example 4: List Providers ===")
    
    downloader = VideoDownloader()
    providers = downloader.list_providers()
    
    print("Available providers:")
    for provider in providers:
        print(f"  - {provider}")


def example_error_handling():
    """Example: Comprehensive error handling."""
    print("\n=== Example 5: Error Handling ===")
    
    downloader = VideoDownloader(output_dir='./downloads')
    
    # Test unsupported URL
    invalid_url = 'not-a-valid-url'
    
    try:
        result = downloader.download(invalid_url, 'test')
        if not result['success']:
            print(f"✓ Handled gracefully: {result['error']}")
    except UnsupportedPlatformError as e:
        print(f"✓ Caught unsupported platform: {e}")
    except DownloadError as e:
        print(f"✓ Caught download error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_multiple_videos():
    """Example: Download multiple videos."""
    print("\n=== Example 6: Multiple Downloads ===")
    
    downloader = VideoDownloader(output_dir='./downloads')
    
    videos = [
        {'url': 'https://www.instagram.com/p/video1/', 'title': 'video_1'},
        {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'video_2'},
        {'url': 'https://www.tiktok.com/@user/video/123', 'title': 'video_3'},
    ]
    
    for video in videos:
        print(f"\nDownloading: {video['title']}")
        try:
            result = downloader.download(video['url'], video['title'])
            if result['success']:
                print(f"  ✓ Success: {result['filepath']}")
            else:
                print(f"  ✗ Failed: {result['error']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Enhanced Video Downloader - Example Usage")
    print("=" * 60)
    
    # Note: These examples use placeholder URLs
    # Replace with real URLs to test actual downloads
    
    print("\nNOTE: Examples use placeholder URLs.")
    print("Replace with real URLs to test actual functionality.\n")
    
    example_list_providers()
    # Uncomment to run other examples:
    # example_basic_download()
    # example_extract_info()
    # example_duplicate_prevention()
    # example_error_handling()
    # example_multiple_videos()


if __name__ == '__main__':
    main()
