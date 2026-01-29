"""
Video Downloader Module

A modular, extensible video downloader supporting multiple platforms.
"""

from .core import VideoDownloader
from .exceptions import (
    DownloadError,
    UnsupportedPlatformError,
    ExtractionError,
    DuplicateFileError
)

__all__ = [
    'VideoDownloader',
    'DownloadError',
    'UnsupportedPlatformError',
    'ExtractionError',
    'DuplicateFileError'
]
