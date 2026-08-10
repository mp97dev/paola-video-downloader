"""
Video Downloader Module

A modular, extensible video downloader supporting multiple platforms.
"""

from pathlib import Path

from .core import VideoDownloader
from .exceptions import (
    DownloadError,
    UnsupportedPlatformError,
    ExtractionError,
    DuplicateFileError,
    AuthenticationRequiredError
)


def _read_version() -> str:
    """Read the project version from the VERSION file at the repo root."""
    version_file = Path(__file__).resolve().parents[2] / 'VERSION'
    try:
        return version_file.read_text(encoding='utf-8').strip() or 'unknown'
    except OSError:
        return 'unknown'


__version__ = _read_version()

__all__ = [
    '__version__',
    'VideoDownloader',
    'DownloadError',
    'UnsupportedPlatformError',
    'ExtractionError',
    'DuplicateFileError',
    'AuthenticationRequiredError'
]
