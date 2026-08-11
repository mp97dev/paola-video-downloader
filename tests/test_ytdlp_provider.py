"""Unit tests for the yt-dlp provider helpers."""

import unittest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from downloader.exceptions import AuthenticationRequiredError, DownloadError
from downloader.providers.ytdlp_provider import (
    YtDlpProvider,
    _is_auth_error,
    _is_rate_limited,
)


class TestResolveFilepath(unittest.TestCase):
    """Tests for deriving the written path from a yt-dlp info dict."""

    def test_prefers_requested_downloads_filepath(self):
        info = {
            '_filename': 'video.webm',
            'requested_downloads': [{'filepath': 'video.mp4'}],
        }
        self.assertEqual(YtDlpProvider._resolve_filepath(info), 'video.mp4')

    def test_falls_back_to_download_underscore_filename(self):
        info = {'requested_downloads': [{'_filename': 'video.mkv'}]}
        self.assertEqual(YtDlpProvider._resolve_filepath(info), 'video.mkv')

    def test_falls_back_to_top_level_filename(self):
        info = {'_filename': 'video.mp4'}
        self.assertEqual(YtDlpProvider._resolve_filepath(info), 'video.mp4')

    def test_unwraps_playlist_entries(self):
        info = {
            '_type': 'playlist',
            'entries': [None, {'requested_downloads': [{'filepath': 'first.mp4'}]}],
        }
        self.assertEqual(YtDlpProvider._resolve_filepath(info), 'first.mp4')

    def test_unwraps_multi_video_entries(self):
        # yt-dlp labels multi-part posts (Instagram carousels) `multi_video`
        info = {
            '_type': 'multi_video',
            'entries': [{'requested_downloads': [{'filepath': 'part1.mp4'}]}],
        }
        self.assertEqual(YtDlpProvider._resolve_filepath(info), 'part1.mp4')

    def test_skips_entries_without_a_resolvable_path(self):
        info = {
            '_type': 'multi_video',
            'entries': [None, {'id': 'no-download-here'}, {'_filename': 'second.mp4'}],
        }
        self.assertEqual(YtDlpProvider._resolve_filepath(info), 'second.mp4')

    def test_unwraps_nested_containers(self):
        info = {
            '_type': 'playlist',
            'entries': [{
                '_type': 'multi_video',
                'entries': [{'requested_downloads': [{'filepath': 'nested.mp4'}]}],
            }],
        }
        self.assertEqual(YtDlpProvider._resolve_filepath(info), 'nested.mp4')

    def test_handles_titles_containing_glob_characters(self):
        # A literal path that would not match itself when treated as a glob
        path = '/tmp/la forza del [triangolo].mp4'
        info = {'requested_downloads': [{'filepath': path}]}
        self.assertEqual(YtDlpProvider._resolve_filepath(info), path)

    def test_returns_none_for_empty_info(self):
        self.assertIsNone(YtDlpProvider._resolve_filepath(None))
        self.assertIsNone(YtDlpProvider._resolve_filepath({}))
        self.assertIsNone(YtDlpProvider._resolve_filepath({'_type': 'playlist', 'entries': []}))
        self.assertIsNone(YtDlpProvider._resolve_filepath({'_type': 'multi_video'}))


class TestAuthErrorDetection(unittest.TestCase):
    """Tests for telling a hard refusal apart from a throttle."""

    INSTAGRAM_AMBIGUOUS = (
        'ERROR: [Instagram] Requested content is not available, '
        'rate-limit reached or login required'
    )

    def test_ambiguous_instagram_message_is_treated_as_a_throttle(self):
        # It names login *and* rate limiting, so it must go through the retry loop
        # rather than aborting on the first attempt.
        self.assertTrue(_is_rate_limited(self.INSTAGRAM_AMBIGUOUS))
        self.assertFalse(_is_auth_error(self.INSTAGRAM_AMBIGUOUS))

    def test_detects_unambiguous_login_requirement(self):
        self.assertTrue(_is_auth_error('ERROR: [youtube] Sign in to confirm you are not a bot'))
        self.assertTrue(_is_auth_error('Login required: use --cookies'))

    def test_detects_private_account(self):
        self.assertTrue(_is_auth_error('This account is private'))

    def test_detects_http_429(self):
        self.assertTrue(_is_rate_limited('HTTP Error 429: Too Many Requests'))

    def test_ignores_transient_network_errors(self):
        self.assertFalse(_is_auth_error('Unable to download webpage: timed out'))
        self.assertFalse(_is_auth_error('HTTP Error 500: Internal Server Error'))
        self.assertFalse(_is_rate_limited('HTTP Error 500: Internal Server Error'))


class TestFormatSelector(unittest.TestCase):
    """Merged formats may only be offered when ffmpeg can do the merging."""

    def test_offers_merged_formats_when_ffmpeg_is_present(self):
        with patch('downloader.providers.ytdlp_provider.shutil.which',
                   return_value='/usr/bin/ffmpeg'):
            self.assertIn('bv*+ba', YtDlpProvider._format_selector())

    def test_omits_merged_formats_without_ffmpeg(self):
        with patch('downloader.providers.ytdlp_provider.shutil.which', return_value=None):
            selector = YtDlpProvider._format_selector()
        self.assertNotIn('+ba', selector)
        self.assertEqual(selector, 'best[ext=mp4]/best')


class TestRateLimitRetry(unittest.TestCase):
    """A throttle gets the backoff loop; only an exhausted one demands cookies."""

    def _provider(self):
        return YtDlpProvider(max_retries=3, retry_delay=0)

    def _patched_ydl(self, side_effect):
        """Patch YoutubeDL so extract_info raises `side_effect` on every attempt."""
        ydl = MagicMock()
        ydl.__enter__.return_value.extract_info.side_effect = side_effect
        return patch('downloader.providers.ytdlp_provider.yt_dlp.YoutubeDL', return_value=ydl)

    def test_throttle_is_retried_then_reported_as_auth_required(self):
        error = Exception(TestAuthErrorDetection.INSTAGRAM_AMBIGUOUS)
        with self._patched_ydl(error) as ydl_cls, \
             patch('downloader.providers.ytdlp_provider.time.sleep'):
            with self.assertRaises(AuthenticationRequiredError):
                self._provider().download('https://instagram.com/p/x', output_path='.')
            self.assertEqual(ydl_cls.call_count, 3)

    def test_hard_refusal_aborts_on_the_first_attempt(self):
        error = Exception('ERROR: [youtube] Sign in to confirm you are not a bot')
        with self._patched_ydl(error) as ydl_cls, \
             patch('downloader.providers.ytdlp_provider.time.sleep'):
            with self.assertRaises(AuthenticationRequiredError):
                self._provider().download('https://youtube.com/watch?v=x', output_path='.')
            self.assertEqual(ydl_cls.call_count, 1)

    def test_generic_failure_still_raises_download_error(self):
        with self._patched_ydl(Exception('HTTP Error 500: Internal Server Error')), \
             patch('downloader.providers.ytdlp_provider.time.sleep'):
            with self.assertRaises(DownloadError):
                self._provider().download('https://example.com/v', output_path='.')


if __name__ == '__main__':
    unittest.main()
