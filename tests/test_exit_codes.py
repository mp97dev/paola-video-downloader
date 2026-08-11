"""Tests for the exit-code contract the CI nightly retry depends on."""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import app
from downloader.exceptions import (
    DownloadError,
    UnsupportedPlatformError,
    DuplicateFileError,
    AuthenticationRequiredError,
)


class TestExitCodes(unittest.TestCase):
    """main() must exit 2 only when a newer yt-dlp could plausibly help."""

    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({'title': 'test', 'link': 'https://example.com/video'}, f)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def _run_expecting_exit(self):
        with self.assertRaises(SystemExit) as ctx:
            app.main()
        return ctx.exception.code

    def test_download_failure_result_is_retryable(self):
        with patch.object(app.VideoDownloader, 'download',
                          return_value={'success': False, 'error': 'boom'}):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_STALE_EXTRACTOR)

    def test_download_error_is_retryable(self):
        with patch.object(app.VideoDownloader, 'download',
                          side_effect=DownloadError('extractor broke')):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_STALE_EXTRACTOR)

    def test_auth_required_is_not_retryable(self):
        with patch.object(app.VideoDownloader, 'download',
                          side_effect=AuthenticationRequiredError('login required')):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_AUTH_REQUIRED)

    def test_unsupported_platform_is_not_retryable(self):
        with patch.object(app.VideoDownloader, 'download',
                          side_effect=UnsupportedPlatformError('nope')):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_ERROR)

    def test_unsupported_platform_from_real_core_is_not_retryable(self):
        # Exercise the path core actually produces: no provider claims the URL.
        # It must not be flattened into a {'success': False} result, which app.py
        # would report as the retryable exit 2.
        from downloader.providers import BaseProvider

        class RefusingProvider(BaseProvider):
            @property
            def name(self):
                return 'refusing'

            def supports(self, url):
                return False

            def extract_info(self, url):
                return {}

            def download(self, url, output_path, title=None):
                raise AssertionError('should never be reached')

        original_init = app.VideoDownloader.__init__

        def only_refusing(self, *args, **kwargs):
            kwargs['providers'] = [RefusingProvider()]
            original_init(self, *args, **kwargs)

        with patch.object(app.VideoDownloader, '__init__', only_refusing):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_ERROR)

    def test_duplicate_file_is_not_retryable(self):
        with patch.object(app.VideoDownloader, 'download',
                          side_effect=DuplicateFileError('exists')):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_ERROR)

    def test_unexpected_error_is_not_retryable(self):
        with patch.object(app.VideoDownloader, 'download',
                          side_effect=RuntimeError('weird')):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_ERROR)

    def test_missing_data_json_is_not_retryable(self):
        os.remove('data.json')
        self.assertEqual(self._run_expecting_exit(), app.EXIT_ERROR)

    def test_failed_upload_fails_the_run(self):
        # A download that succeeds but never reaches Drive must not report success,
        # and must not trigger the nightly retry.
        with patch.object(app.VideoDownloader, 'download',
                          return_value={'success': True, 'filepath': 'test.mp4'}), \
             patch.object(app, 'sendVideo', return_value=None):
            self.assertEqual(self._run_expecting_exit(), app.EXIT_ERROR)

    def test_successful_run_does_not_exit(self):
        with patch.object(app.VideoDownloader, 'download',
                          return_value={'success': True, 'filepath': 'test.mp4'}), \
             patch.object(app, 'sendVideo', return_value='drive-file-id'):
            self.assertIsNone(app.main())


class TestAuthErrorPropagation(unittest.TestCase):
    """core.download() must not flatten auth errors into a generic failure dict."""

    def test_authentication_error_propagates_through_core(self):
        from downloader import VideoDownloader
        from downloader.providers import BaseProvider

        class AuthFailingProvider(BaseProvider):
            @property
            def name(self):
                return 'auth-failing'

            def supports(self, url):
                return True

            def extract_info(self, url):
                return {}

            def download(self, url, output_path, title=None):
                raise AuthenticationRequiredError('login required')

        with tempfile.TemporaryDirectory() as tmp:
            downloader = VideoDownloader(
                output_dir=tmp,
                prevent_duplicates=False,
                providers=[AuthFailingProvider()],
            )
            with self.assertRaises(AuthenticationRequiredError):
                downloader.download('https://example.com/v', 'title')


if __name__ == '__main__':
    unittest.main()
