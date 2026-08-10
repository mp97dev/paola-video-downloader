"""Custom exceptions for the video downloader."""


class DownloadError(Exception):
    """Base exception for download-related errors."""
    pass


class UnsupportedPlatformError(DownloadError):
    """Raised when a platform is not supported."""
    pass


class ExtractionError(DownloadError):
    """Raised when video information extraction fails."""
    pass


class DuplicateFileError(DownloadError):
    """Raised when attempting to download a file that already exists."""
    pass


class NetworkError(DownloadError):
    """Raised when network-related issues occur."""
    pass


class AuthenticationRequiredError(DownloadError):
    """Raised when the platform refuses anonymous access (login or rate limit)."""
    pass
