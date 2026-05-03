"""Generic provider using yt-dlp for broad platform support."""

import logging
import os
from pathlib import Path
from typing import Dict, Optional
import time

from .base import BaseProvider
from ..exceptions import ExtractionError, DownloadError, NetworkError
from ..utils import sanitize_filename

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

logger = logging.getLogger(__name__)


class YtDlpProvider(BaseProvider):
    """
    Generic provider using yt-dlp for downloading videos.
    
    Supports Instagram, YouTube, TikTok, Facebook, Twitter, and many more platforms.
    Handles short-form content like reels, shorts, and stories.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the yt-dlp provider.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
        """
        if yt_dlp is None:
            raise ImportError("yt-dlp is required for YtDlpProvider. Install with: pip install yt-dlp")
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    @property
    def name(self) -> str:
        """Return the provider name."""
        return "yt-dlp"
    
    def supports(self, url: str) -> bool:
        """
        Check if yt-dlp supports the given URL.
        
        yt-dlp supports a wide range of platforms, so we'll do a basic URL validation.
        """
        # Basic URL validation
        if not url or not isinstance(url, str):
            return False
        
        # Check if it looks like a valid URL
        url_lower = url.lower()
        return url_lower.startswith(('http://', 'https://'))
    
    def extract_info(self, url: str) -> Dict:
        """
        Extract video information using yt-dlp.
        
        Args:
            url: The video URL
            
        Returns:
            Dictionary with video metadata
            
        Raises:
            ExtractionError: If extraction fails
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'video'),
                    'url': info.get('url'),
                    'ext': info.get('ext', 'mp4'),
                    'duration': info.get('duration'),
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                    'thumbnail': info.get('thumbnail'),
                }
        except Exception as e:
            logger.error(f"Failed to extract info from {url}: {e}")
            raise ExtractionError(f"Failed to extract video information: {e}")
    
    def download(self, url: str, output_path: str = '.', title: Optional[str] = None) -> str:
        """
        Download video using yt-dlp with retry logic.

        Args:
            url: The video URL
            output_path: Directory to save the video
            title: Optional custom title for the file

        Returns:
            Path to the downloaded file

        Raises:
            DownloadError: If download fails after all retries
        """
        import glob

        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Sanitize filename — no extension added here; yt-dlp fills it via %(ext)s
        safe_title = sanitize_filename(title if title else 'video')
        output_base = os.path.join(output_path, safe_title)

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_base + '.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
            'retries': self.max_retries,
            'fragment_retries': self.max_retries,
            'http_chunk_size': 10485760,  # 10MB chunks
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        # Optional cookies file for platforms that require authentication (e.g. Instagram, Facebook)
        cookies_file = os.environ.get('COOKIES_FILE')
        if cookies_file and os.path.exists(cookies_file):
            ydl_opts['cookiefile'] = cookies_file
            logger.info(f"Using cookies file: {cookies_file}")

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Download attempt {attempt + 1}/{self.max_retries} for {url}")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Find the file yt-dlp created (it sets the extension)
                matches = glob.glob(output_base + '.*')
                if matches:
                    filepath = matches[0]
                    logger.info(f"Successfully downloaded to {filepath}")
                    return filepath

                raise DownloadError("Download completed but file not found")

            except DownloadError:
                raise
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

        # All retries failed
        error_msg = f"Failed to download after {self.max_retries} attempts: {last_error}"
        logger.error(error_msg)
        raise DownloadError(error_msg)
