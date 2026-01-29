"""Base provider interface for video downloaders."""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseProvider(ABC):
    """Abstract base class for video download providers."""
    
    @abstractmethod
    def supports(self, url: str) -> bool:
        """
        Check if this provider supports the given URL.
        
        Args:
            url: The video URL to check
            
        Returns:
            True if this provider can handle the URL, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_info(self, url: str) -> Dict:
        """
        Extract video information from the URL.
        
        Args:
            url: The video URL
            
        Returns:
            Dictionary containing video metadata:
                - title: Video title
                - url: Download URL
                - ext: File extension
                - duration: Video duration (optional)
                - description: Video description (optional)
                
        Raises:
            ExtractionError: If extraction fails
        """
        pass
    
    @abstractmethod
    def download(self, url: str, output_path: str, title: Optional[str] = None) -> str:
        """
        Download video from the given URL.
        
        Args:
            url: The video URL
            output_path: Directory to save the video
            title: Optional custom title for the file
            
        Returns:
            Path to the downloaded file
            
        Raises:
            DownloadError: If download fails
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass
