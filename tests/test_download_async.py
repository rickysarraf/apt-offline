#!/usr/bin/env python3
"""
Unit tests for async and sync download functionality.

These tests exercise both the async and sync download paths using a local HTTP server.
The async path tests are skipped if aiohttp is not installed.
"""

import asyncio
import http.server
import os
import socketserver
import sys
import tempfile
import threading
import time
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apt_offline_core.AptOfflineCoreLib import (
    AIOHTTP_AVAILABLE,
    GenericDownloadFunction,
)
from apt_offline_core import AptOfflineLib


class TestDownloader(AptOfflineLib.ProgressBar, GenericDownloadFunction):
    """Test downloader class with minimal progress bar implementation."""

    def __init__(self):
        AptOfflineLib.ProgressBar.__init__(self, width=50, total_items=0)
        self.progress_updates = []
        self.items_added = []
        self.completed_count = 0

    def display(self):
        """Suppress progress display during tests."""
        pass

    def addItem(self, size):
        """Track items added for testing."""
        self.items_added.append(size)
        super().addItem(size)

    def updateValue(self, value):
        """Track progress updates for testing."""
        self.progress_updates.append(value)
        super().updateValue(value)

    def completed(self):
        """Track completion calls for testing."""
        self.completed_count += 1
        super().completed()


class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler that serves test content."""

    test_content = {}

    def do_GET(self):
        """Handle GET requests with test content."""
        path = self.path.lstrip("/")
        if path in self.test_content:
            content = self.test_content[path]
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        """Suppress server logging during tests."""
        pass


class TestDownloadFunctionBase(unittest.TestCase):
    """Base test class that sets up a local HTTP server."""

    @classmethod
    def setUpClass(cls):
        """Set up a local HTTP server for testing."""
        # Create test content
        cls.small_content = b"Hello, World! This is a small test file."
        cls.medium_content = b"X" * 10000  # 10KB
        cls.large_content = b"Y" * 100000  # 100KB

        SimpleHTTPRequestHandler.test_content = {
            "small.txt": cls.small_content,
            "medium.bin": cls.medium_content,
            "large.bin": cls.large_content,
        }

        # Start HTTP server in a separate thread
        cls.server = socketserver.TCPServer(
            ("127.0.0.1", 0), SimpleHTTPRequestHandler
        )
        cls.server_address = cls.server.server_address
        cls.server_url = f"http://{cls.server_address[0]}:{cls.server_address[1]}"

        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Give server time to start
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        """Shut down the HTTP server."""
        cls.server.shutdown()
        cls.server_thread.join(timeout=1)

    def setUp(self):
        """Create a temporary directory for downloads."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_dir)
        # Clean up any downloaded files
        for f in os.listdir(self.temp_dir):
            os.unlink(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)


class TestSyncDownload(TestDownloadFunctionBase):
    """Tests for the synchronous download implementation."""

    def test_sync_download_small_file(self):
        """Test sync download of a small file."""
        downloader = TestDownloader()
        url = f"{self.server_url}/small.txt"
        filename = "small_download.txt"

        result = downloader._download_from_web_sync(url, filename, self.temp_dir)

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.small_content)

    def test_sync_download_medium_file(self):
        """Test sync download of a medium-sized file."""
        downloader = TestDownloader()
        url = f"{self.server_url}/medium.bin"
        filename = "medium_download.bin"

        result = downloader._download_from_web_sync(url, filename, self.temp_dir)

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.medium_content)

    def test_sync_download_large_file(self):
        """Test sync download of a large file."""
        downloader = TestDownloader()
        url = f"{self.server_url}/large.bin"
        filename = "large_download.bin"

        result = downloader._download_from_web_sync(url, filename, self.temp_dir)

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.large_content)

    def test_sync_download_404_error(self):
        """Test sync download handles 404 errors gracefully."""
        downloader = TestDownloader()
        url = f"{self.server_url}/nonexistent.txt"
        filename = "nonexistent_download.txt"

        result = downloader._download_from_web_sync(url, filename, self.temp_dir)

        self.assertFalse(result)

    def test_sync_download_progress_tracking(self):
        """Test that sync download tracks progress correctly."""
        downloader = TestDownloader()
        url = f"{self.server_url}/medium.bin"
        filename = "progress_test.bin"

        result = downloader._download_from_web_sync(url, filename, self.temp_dir)

        self.assertTrue(result)
        # Check that progress was tracked
        self.assertGreater(len(downloader.items_added), 0)
        self.assertGreater(len(downloader.progress_updates), 0)
        self.assertEqual(downloader.completed_count, 1)


@unittest.skipUnless(AIOHTTP_AVAILABLE, "aiohttp is not installed")
class TestAsyncDownload(TestDownloadFunctionBase):
    """Tests for the asynchronous download implementation."""

    def test_async_download_small_file(self):
        """Test async download of a small file."""
        async def run_test():
            downloader = TestDownloader()
            url = f"{self.server_url}/small.txt"
            filename = "small_async_download.txt"
            return await downloader._download_from_web_async(
                url, filename, self.temp_dir
            )

        result = asyncio.run(run_test())

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, "small_async_download.txt")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.small_content)

    def test_async_download_medium_file(self):
        """Test async download of a medium-sized file."""
        async def run_test():
            downloader = TestDownloader()
            url = f"{self.server_url}/medium.bin"
            filename = "medium_async_download.bin"
            return await downloader._download_from_web_async(
                url, filename, self.temp_dir
            )

        result = asyncio.run(run_test())

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, "medium_async_download.bin")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.medium_content)

    def test_async_download_large_file(self):
        """Test async download of a large file."""
        async def run_test():
            downloader = TestDownloader()
            url = f"{self.server_url}/large.bin"
            filename = "large_async_download.bin"
            return await downloader._download_from_web_async(
                url, filename, self.temp_dir
            )

        result = asyncio.run(run_test())

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, "large_async_download.bin")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.large_content)

    def test_async_download_404_error(self):
        """Test async download handles 404 errors gracefully."""
        async def run_test():
            downloader = TestDownloader()
            url = f"{self.server_url}/nonexistent.txt"
            filename = "nonexistent_async_download.txt"
            return await downloader._download_from_web_async(
                url, filename, self.temp_dir
            )

        result = asyncio.run(run_test())

        self.assertFalse(result)
        # Ensure no partial file was left behind
        filepath = os.path.join(self.temp_dir, "nonexistent_async_download.txt")
        self.assertFalse(os.path.exists(filepath))

    def test_async_download_progress_tracking(self):
        """Test that async download tracks progress correctly."""
        async def run_test():
            downloader = TestDownloader()
            url = f"{self.server_url}/medium.bin"
            filename = "progress_async_test.bin"
            result = await downloader._download_from_web_async(
                url, filename, self.temp_dir
            )
            return result, downloader

        result, downloader = asyncio.run(run_test())

        self.assertTrue(result)
        # Check that progress was tracked
        self.assertGreater(len(downloader.items_added), 0)
        self.assertGreater(len(downloader.progress_updates), 0)
        self.assertEqual(downloader.completed_count, 1)

    def test_async_concurrent_downloads(self):
        """Test multiple concurrent async downloads."""
        async def run_test():
            tasks = []
            for i, path in enumerate(["small.txt", "medium.bin", "large.bin"]):
                downloader = TestDownloader()
                url = f"{self.server_url}/{path}"
                filename = f"concurrent_{i}_{path}"
                tasks.append(
                    downloader._download_from_web_async(url, filename, self.temp_dir)
                )
            return await asyncio.gather(*tasks)

        results = asyncio.run(run_test())

        self.assertEqual(len(results), 3)
        self.assertTrue(all(results))


class TestDownloadWrapper(TestDownloadFunctionBase):
    """Tests for the download_from_web wrapper method."""

    def test_wrapper_downloads_file(self):
        """Test that the wrapper successfully downloads a file."""
        downloader = TestDownloader()
        url = f"{self.server_url}/small.txt"
        filename = "wrapper_download.txt"

        result = downloader.download_from_web(url, filename, self.temp_dir)

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, "rb") as f:
            content = f.read()
        self.assertEqual(content, self.small_content)

    def test_wrapper_handles_errors(self):
        """Test that the wrapper handles errors gracefully."""
        downloader = TestDownloader()
        url = f"{self.server_url}/nonexistent.txt"
        filename = "wrapper_error_download.txt"

        result = downloader.download_from_web(url, filename, self.temp_dir)

        self.assertFalse(result)

    @unittest.skipUnless(AIOHTTP_AVAILABLE, "aiohttp is not installed")
    def test_wrapper_uses_async_when_available(self):
        """Test that the wrapper uses async path when aiohttp is available."""
        # This is more of a smoke test - we can't easily verify which path was used
        # without mocking, but we can verify it still works
        downloader = TestDownloader()
        url = f"{self.server_url}/medium.bin"
        filename = "wrapper_async_test.bin"

        result = downloader.download_from_web(url, filename, self.temp_dir)

        self.assertTrue(result)
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))


class TestAiohttpAvailability(unittest.TestCase):
    """Tests for checking aiohttp availability."""

    def test_aiohttp_availability_flag(self):
        """Test that AIOHTTP_AVAILABLE flag is correctly set."""
        try:
            import aiohttp
            self.assertTrue(AIOHTTP_AVAILABLE)
        except ImportError:
            self.assertFalse(AIOHTTP_AVAILABLE)


if __name__ == "__main__":
    unittest.main()
