"""Generic provider using yt-dlp for broad platform support."""

import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Optional
import time

from .base import BaseProvider
from ..exceptions import (
    ExtractionError,
    DownloadError,
    NetworkError,
    AuthenticationRequiredError,
)
from ..utils import sanitize_filename

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

logger = logging.getLogger(__name__)

# Fragments of yt-dlp error messages that mean "the platform refused anonymous
# access" rather than "something went wrong". Retrying these in-process never
# helps: the run needs cookies.
_AUTH_ERROR_MARKERS = (
    'login required',
    'sign in to confirm',
    'private video',
    'this account is private',
    'you need to log in',
    'use --cookies',
)

# Instagram folds a throttle, a deleted post and a missing login into one message:
#   "Requested content is not available, rate-limit reached or login required"
# A throttle is the one failure here that a short wait genuinely fixes, so these
# get the full backoff loop and only become an auth error once attempts run out.
_RATE_LIMIT_MARKERS = (
    'rate-limit reached',
    'requested content is not available',
    'http error 429',
    'too many requests',
)


def _is_rate_limited(message: str) -> bool:
    """Return True if the error may just be throttling, and is worth retrying."""
    lowered = message.lower()
    return any(marker in lowered for marker in _RATE_LIMIT_MARKERS)


def _is_auth_error(message: str) -> bool:
    """Return True if the error is a refusal that retrying can never fix."""
    # A message that also mentions throttling is ambiguous; let the retry loop
    # settle it rather than demanding cookies on the first attempt.
    if _is_rate_limited(message):
        return False

    lowered = message.lower()
    return any(marker in lowered for marker in _AUTH_ERROR_MARKERS)


def _auth_required_message(url: str, error: Exception) -> str:
    """Build the operator-facing message for a refusal that needs cookies."""
    return (
        f"{url} could not be downloaded anonymously: {error}. "
        "Export browser cookies in Netscape format and expose them "
        "via the COOKIES_FILE environment variable (the workflow reads "
        "the base64-encoded COOKIES repository secret)."
    )


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
    
    @staticmethod
    def _resolve_filepath(info: Optional[Dict]) -> Optional[str]:
        """
        Work out the path yt-dlp wrote to from the info dict it returns.

        Args:
            info: The info dict returned by ``extract_info(download=True)``

        Returns:
            The path of the final file, or None if it cannot be determined
        """
        if not info:
            return None

        # Container results wrap the real entries. yt-dlp emits `multi_video` for
        # multi-part posts (e.g. an Instagram carousel) and handles it exactly like
        # a playlist — `requested_downloads` only ever lands on the inner entries.
        if info.get('_type') in ('playlist', 'multi_video'):
            for entry in info.get('entries') or []:
                path = YtDlpProvider._resolve_filepath(entry)
                if path:
                    return path
            return None

        # `requested_downloads` carries the post-processed path (after merging)
        for download in info.get('requested_downloads') or []:
            path = download.get('filepath') or download.get('_filename')
            if path:
                return path

        return info.get('filepath') or info.get('_filename')

    @staticmethod
    def _format_selector() -> str:
        """
        Build the format string, taking local ffmpeg availability into account.

        The video+audio fallbacks have to be merged, and yt-dlp aborts the whole
        download when it selects a merged format without ffmpeg present — it does
        not fall through to the next candidate. So only offer them when merging
        can actually happen.
        """
        if shutil.which('ffmpeg'):
            return 'best[ext=mp4]/bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best'

        logger.warning(
            "ffmpeg not found: falling back to pre-muxed formats only. "
            "DASH-only posts (common on Instagram) may fail to download. "
            "Install ffmpeg to enable video+audio merging."
        )
        return 'best[ext=mp4]/best'

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
            AuthenticationRequiredError: If the platform refuses anonymous access
            DownloadError: If download fails after all retries
        """
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Sanitize filename — no extension added here; yt-dlp fills it via %(ext)s
        safe_title = sanitize_filename(title if title else 'video')
        output_base = os.path.join(output_path, safe_title)

        # Configure yt-dlp options.
        # Format selection falls back progressively: a ready-made mp4 first, then
        # separate video+audio streams merged locally. Platforms such as Instagram
        # serve DASH-only streams for some posts, where a bare `best` finds nothing.
        ydl_opts = {
            'format': self._format_selector(),
            'outtmpl': output_base + '.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
            'retries': self.max_retries,
            'fragment_retries': self.max_retries,
            'http_chunk_size': 10485760,  # 10MB chunks
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
                    info = ydl.extract_info(url, download=True)

                # Ask yt-dlp where it actually put the file rather than guessing:
                # the extension is decided at download time and post-processors
                # (e.g. the mp4 merger) may rename the result.
                filepath = self._resolve_filepath(info)
                if filepath and os.path.exists(filepath):
                    logger.info(f"Successfully downloaded to {filepath}")
                    return filepath

                if filepath:
                    raise DownloadError(
                        f"Download reported success but the file is missing: {filepath}"
                    )
                raise DownloadError(
                    "Download reported success but yt-dlp named no output file "
                    f"(expected something under {output_base}.*)"
                )

            except DownloadError:
                raise
            except Exception as e:
                if _is_auth_error(str(e)):
                    raise AuthenticationRequiredError(
                        _auth_required_message(url, e)
                    ) from e

                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

        # All retries failed. A throttle that survived the whole backoff loop is no
        # longer plausibly transient — surface it as "needs cookies" so the caller
        # exits 3 and the operator gets the actionable message.
        if last_error is not None and _is_rate_limited(str(last_error)):
            logger.error(f"Still refused after {self.max_retries} attempts: {last_error}")
            raise AuthenticationRequiredError(
                _auth_required_message(url, last_error)
            ) from last_error

        error_msg = f"Failed to download after {self.max_retries} attempts: {last_error}"
        logger.error(error_msg)
        raise DownloadError(error_msg)
