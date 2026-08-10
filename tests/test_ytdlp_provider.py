"""Unit tests for the yt-dlp provider helpers."""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from downloader.providers.ytdlp_provider import YtDlpProvider, _is_auth_error


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

    def test_handles_titles_containing_glob_characters(self):
        # A literal path that would not match itself when treated as a glob
        path = '/tmp/la forza del [triangolo].mp4'
        info = {'requested_downloads': [{'filepath': path}]}
        self.assertEqual(YtDlpProvider._resolve_filepath(info), path)

    def test_returns_none_for_empty_info(self):
        self.assertIsNone(YtDlpProvider._resolve_filepath(None))
        self.assertIsNone(YtDlpProvider._resolve_filepath({}))
        self.assertIsNone(YtDlpProvider._resolve_filepath({'_type': 'playlist', 'entries': []}))


class TestAuthErrorDetection(unittest.TestCase):
    """Tests for recognising login/rate-limit refusals."""

    def test_detects_login_required(self):
        self.assertTrue(_is_auth_error(
            'ERROR: [Instagram] Requested content is not available, '
            'rate-limit reached or login required'
        ))

    def test_detects_private_account(self):
        self.assertTrue(_is_auth_error('This account is private'))

    def test_ignores_transient_network_errors(self):
        self.assertFalse(_is_auth_error('Unable to download webpage: timed out'))
        self.assertFalse(_is_auth_error('HTTP Error 500: Internal Server Error'))


if __name__ == '__main__':
    unittest.main()
