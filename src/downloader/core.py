"""Core video downloader with provider management."""

import logging
import os
from typing import List, Optional, Dict

from .providers import BaseProvider, YtDlpProvider
from .exceptions import UnsupportedPlatformError, DownloadError, DuplicateFileError
from .utils import check_duplicate, sanitize_filename

logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Main video downloader class that manages multiple providers.
    
    This class provides a unified interface for downloading videos from
    various platforms by automatically selecting the appropriate provider.
    """
    
    def __init__(self, 
                 output_dir: str = '.',
                 prevent_duplicates: bool = True,
                 providers: Optional[List[BaseProvider]] = None):
        """
        Initialize the video downloader.
        
        Args:
            output_dir: Directory where videos will be saved
            prevent_duplicates: If True, check for existing files before downloading
            providers: List of provider instances to use. If None, use defaults.
        """
        self.output_dir = output_dir
        self.prevent_duplicates = prevent_duplicates
        
        # Initialize providers
        if providers is None:
            self.providers = [
                YtDlpProvider(max_retries=3, retry_delay=2)
            ]
        else:
            self.providers = providers
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"VideoDownloader initialized with {len(self.providers)} provider(s)")
    
    def _select_provider(self, url: str) -> BaseProvider:
        """
        Select the appropriate provider for the given URL.
        
        Args:
            url: The video URL
            
        Returns:
            The first provider that supports the URL
            
        Raises:
            UnsupportedPlatformError: If no provider supports the URL
        """
        for provider in self.providers:
            if provider.supports(url):
                logger.info(f"Selected provider: {provider.name}")
                return provider
        
        raise UnsupportedPlatformError(
            f"No provider supports URL: {url}. "
            f"Available providers: {[p.name for p in self.providers]}"
        )
    
    def download(self, url: str, title: Optional[str] = None) -> Dict:
        """
        Download a video from the given URL.
        
        Args:
            url: The video URL
            title: Optional custom title for the file
            
        Returns:
            Dictionary with download results:
                - success: Boolean indicating success
                - filepath: Path to downloaded file (if successful)
                - error: Error message (if failed)
                - provider: Name of provider used
                
        Raises:
            UnsupportedPlatformError: If URL is not supported
            DuplicateFileError: If file exists and prevent_duplicates is True
            DownloadError: If download fails
        """
        logger.info(f"Starting download for URL: {url}")
        
        # Select provider
        try:
            provider = self._select_provider(url)
        except UnsupportedPlatformError as e:
            logger.error(str(e))
            return {
                'success': False,
                'error': str(e),
                'provider': None
            }
        
        # Check for duplicates if enabled
        if self.prevent_duplicates and title:
            safe_title = sanitize_filename(title)
            # Check common video extensions
            for ext in ['.mp4', '.webm', '.mkv', '.m4a']:
                potential_file = safe_title if safe_title.endswith(ext) else f"{safe_title}{ext}"
                existing = check_duplicate(potential_file, self.output_dir)
                if existing:
                    error_msg = f"File already exists: {existing}"
                    logger.warning(error_msg)
                    if self.prevent_duplicates:
                        raise DuplicateFileError(error_msg)
        
        # Download the video
        try:
            filepath = provider.download(url, self.output_dir, title)
            
            result = {
                'success': True,
                'filepath': filepath,
                'provider': provider.name
            }
            
            logger.info(f"Download successful: {filepath}")
            return result
            
        except Exception as e:
            error_msg = f"Download failed: {e}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'error': str(e),
                'provider': provider.name
            }
    
    def extract_info(self, url: str) -> Dict:
        """
        Extract video information without downloading.
        
        Args:
            url: The video URL
            
        Returns:
            Dictionary with video metadata
            
        Raises:
            UnsupportedPlatformError: If URL is not supported
        """
        provider = self._select_provider(url)
        return provider.extract_info(url)
    
    def add_provider(self, provider: BaseProvider):
        """
        Add a new provider to the downloader.
        
        Args:
            provider: Provider instance to add
        """
        self.providers.append(provider)
        logger.info(f"Added provider: {provider.name}")
    
    def list_providers(self) -> List[str]:
        """
        List all registered providers.
        
        Returns:
            List of provider names
        """
        return [p.name for p in self.providers]
