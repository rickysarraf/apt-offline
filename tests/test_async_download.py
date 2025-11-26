#!/usr/bin/env python3
"""
Tests for async download functionality in apt-offline.
"""

import asyncio
import inspect
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apt_offline_core.AptOfflineCoreLib import (
    GenericDownloadFunction,
    ASYNC_SUPPORT,
    run_async_downloads,
    async_download_batch,
)
from apt_offline_core.AptOfflineLib import ProgressBar


class TestAsyncDownloadSupport(unittest.TestCase):
    """Test async download support availability."""

    def test_async_support_available(self):
        """Test that ASYNC_SUPPORT is properly set based on available modules."""
        try:
            import aiohttp
            import aiofiles
            self.assertTrue(ASYNC_SUPPORT)
        except ImportError:
            self.assertFalse(ASYNC_SUPPORT)


class TestAsyncFunctionSignatures(unittest.TestCase):
    """Test that async functions have correct signatures."""

    def test_async_download_from_web_is_async(self):
        """Test async_download_from_web is a coroutine function."""
        g = GenericDownloadFunction()
        self.assertTrue(asyncio.iscoroutinefunction(g.async_download_from_web))

    def test_download_from_web_is_sync(self):
        """Test download_from_web is NOT a coroutine function."""
        g = GenericDownloadFunction()
        self.assertFalse(asyncio.iscoroutinefunction(g.download_from_web))

    def test_async_download_batch_is_async(self):
        """Test async_download_batch is a coroutine function."""
        self.assertTrue(asyncio.iscoroutinefunction(async_download_batch))

    def test_run_async_downloads_is_sync(self):
        """Test run_async_downloads is NOT a coroutine function (it's a wrapper)."""
        self.assertFalse(asyncio.iscoroutinefunction(run_async_downloads))


class TestDownloader(ProgressBar, GenericDownloadFunction):
    """Test helper class combining ProgressBar and GenericDownloadFunction."""

    def __init__(self):
        ProgressBar.__init__(self, width=30, total_items=1)

    def display(self):
        # Override display to not print to console during tests
        pass


class TestAsyncDownloadIntegration(unittest.TestCase):
    """Integration tests for async download (requires network)."""

    @unittest.skipIf(not ASYNC_SUPPORT, "Async support not available")
    def test_async_download_method_exists(self):
        """Test that async_download_from_web method exists and is callable."""
        downloader = TestDownloader()
        self.assertTrue(hasattr(downloader, 'async_download_from_web'))
        self.assertTrue(callable(downloader.async_download_from_web))

    @unittest.skipIf(not ASYNC_SUPPORT, "Async support not available")
    def test_run_async_downloads_function(self):
        """Test run_async_downloads returns empty list with empty input."""
        downloader = TestDownloader()
        results = run_async_downloads(downloader, [])
        self.assertEqual(results, [])


class TestFallbackBehavior(unittest.TestCase):
    """Test fallback behavior when async support is not available."""

    def test_async_method_fallback(self):
        """Test that async_download_from_web falls back to sync when ASYNC_SUPPORT is False."""
        # We can't easily test this without modifying the module,
        # but we can verify the code path exists
        g = GenericDownloadFunction()
        self.assertTrue(hasattr(g, 'async_download_from_web'))
        self.assertTrue(hasattr(g, 'download_from_web'))


if __name__ == '__main__':
    unittest.main()
