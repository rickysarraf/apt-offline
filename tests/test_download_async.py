#!/usr/bin/env python3
"""Tests for async download functionality in apt-offline.

These tests verify that both sync and async download paths work correctly.
Async tests are skipped if optional dependencies (aiohttp, aiofiles) are not available.
"""

import functools
import http.server
import os
import shutil
import socketserver
import sys
import tempfile
import threading
import pytest

# Add parent directory to path to import apt_offline_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apt_offline_core.AptOfflineCoreLib import (
    ASYNC_AVAILABLE,
    download_from_web,
    _download_from_web_sync,
    GenericDownloadFunction,
)
from apt_offline_core import AptOfflineLib


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses logging and serves from a specific directory."""
    
    def __init__(self, *args, directory=None, **kwargs):
        # SimpleHTTPRequestHandler supports directory argument in Python 3.7+
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        pass


class DummyProgressBar:
    """Dummy progress bar for testing."""
    
    def __init__(self):
        self.items_added = []
        self.bytes_updated = 0
        self.completed_count = 0
    
    def addItem(self, size):
        self.items_added.append(size)
    
    def updateValue(self, increment):
        self.bytes_updated += increment
    
    def completed(self):
        self.completed_count += 1


class MockDownloader(AptOfflineLib.ProgressBar, GenericDownloadFunction):
    """A mock downloader that inherits from ProgressBar and GenericDownloadFunction."""
    
    def __init__(self):
        AptOfflineLib.ProgressBar.__init__(self, width=80, total_items=1)
        # Track calls for testing
        self.items_added = []
        self.bytes_updated = 0
        self.completed_count = 0
    
    def addItem(self, size):
        self.items_added.append(size)
        super().addItem(size)
    
    def updateValue(self, increment):
        self.bytes_updated += increment
        super().updateValue(increment)
    
    def completed(self):
        self.completed_count += 1
        super().completed()
    
    def display(self):
        # Override to suppress output during tests
        pass


@pytest.fixture(scope='module')
def http_server():
    """Start a local HTTP server for testing."""
    # Create temp directory with test files
    serve_dir = tempfile.mkdtemp(prefix='apt-offline-test-')
    
    # Create test files
    test_content = b'Test content for apt-offline download testing.\n' * 100
    test_file = os.path.join(serve_dir, 'test_file.txt')
    with open(test_file, 'wb') as f:
        f.write(test_content)
    
    # Create a larger test file
    large_content = os.urandom(50000)  # 50KB
    large_file = os.path.join(serve_dir, 'large_file.bin')
    with open(large_file, 'wb') as f:
        f.write(large_content)
    
    # Create handler that serves from specific directory
    handler = functools.partial(QuietHTTPRequestHandler, directory=serve_dir)
    
    server = socketserver.TCPServer(('127.0.0.1', 0), handler)
    port = server.server_address[1]
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    yield {
        'server': server,
        'port': port,
        'base_url': f'http://127.0.0.1:{port}',
        'serve_dir': serve_dir,
        'test_content': test_content,
        'large_content': large_content,
    }
    
    # Cleanup
    server.shutdown()
    shutil.rmtree(serve_dir, ignore_errors=True)


@pytest.fixture
def download_dir():
    """Create a temporary download directory."""
    temp_dir = tempfile.mkdtemp(prefix='apt-offline-download-')
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestSyncDownload:
    """Tests for synchronous download functionality."""
    
    def test_sync_download_success(self, http_server, download_dir):
        """Test successful sync download."""
        url = f'{http_server["base_url"]}/test_file.txt'
        local_file = 'downloaded_test.txt'
        downloader = MockDownloader()
        
        result = _download_from_web_sync(downloader, url, local_file, download_dir)
        
        assert result is True
        downloaded_path = os.path.join(download_dir, local_file)
        assert os.path.exists(downloaded_path)
        
        with open(downloaded_path, 'rb') as f:
            content = f.read()
        assert content == http_server['test_content']
    
    def test_sync_download_large_file(self, http_server, download_dir):
        """Test sync download of larger file."""
        url = f'{http_server["base_url"]}/large_file.bin'
        local_file = 'downloaded_large.bin'
        downloader = MockDownloader()
        
        result = _download_from_web_sync(downloader, url, local_file, download_dir)
        
        assert result is True
        downloaded_path = os.path.join(download_dir, local_file)
        assert os.path.exists(downloaded_path)
        
        with open(downloaded_path, 'rb') as f:
            content = f.read()
        assert content == http_server['large_content']
    
    def test_sync_download_404(self, http_server, download_dir):
        """Test sync download with 404 error."""
        url = f'{http_server["base_url"]}/nonexistent_file.txt'
        local_file = 'should_not_exist.txt'
        downloader = MockDownloader()
        
        result = _download_from_web_sync(downloader, url, local_file, download_dir)
        
        assert result is False
    
    def test_sync_download_progress_callbacks(self, http_server, download_dir):
        """Test that progress callbacks are invoked during sync download."""
        url = f'{http_server["base_url"]}/large_file.bin'
        local_file = 'downloaded_progress.bin'
        downloader = MockDownloader()
        
        result = _download_from_web_sync(downloader, url, local_file, download_dir)
        
        assert result is True
        # Progress should have been reported
        assert len(downloader.items_added) > 0
        assert downloader.bytes_updated > 0
        assert downloader.completed_count == 1


class TestAsyncDownload:
    """Tests for asynchronous download functionality."""
    
    @pytest.mark.skipif(not ASYNC_AVAILABLE, reason='aiohttp/aiofiles not available')
    def test_async_download_success(self, http_server, download_dir):
        """Test successful async download."""
        import asyncio
        from apt_offline_core.AptOfflineCoreLib import _download_from_web_async
        
        url = f'{http_server["base_url"]}/test_file.txt'
        local_file = 'async_downloaded.txt'
        
        progress_data = {'items': [], 'bytes': 0, 'completed': 0}
        progress_callback = {
            'addItem': lambda x: progress_data['items'].append(x),
            'updateValue': lambda x: progress_data.update({'bytes': progress_data['bytes'] + x}),
            'completed': lambda: progress_data.update({'completed': progress_data['completed'] + 1}),
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _download_from_web_async(url, local_file, download_dir, progress_callback)
            )
        finally:
            loop.close()
        
        assert result is True
        downloaded_path = os.path.join(download_dir, local_file)
        assert os.path.exists(downloaded_path)
        
        with open(downloaded_path, 'rb') as f:
            content = f.read()
        assert content == http_server['test_content']
    
    @pytest.mark.skipif(not ASYNC_AVAILABLE, reason='aiohttp/aiofiles not available')
    def test_async_download_large_file(self, http_server, download_dir):
        """Test async download of larger file."""
        import asyncio
        from apt_offline_core.AptOfflineCoreLib import _download_from_web_async
        
        url = f'{http_server["base_url"]}/large_file.bin'
        local_file = 'async_large.bin'
        
        progress_callback = {
            'addItem': lambda x: None,
            'updateValue': lambda x: None,
            'completed': lambda: None,
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _download_from_web_async(url, local_file, download_dir, progress_callback)
            )
        finally:
            loop.close()
        
        assert result is True
        downloaded_path = os.path.join(download_dir, local_file)
        assert os.path.exists(downloaded_path)
        
        with open(downloaded_path, 'rb') as f:
            content = f.read()
        assert content == http_server['large_content']
    
    @pytest.mark.skipif(not ASYNC_AVAILABLE, reason='aiohttp/aiofiles not available')
    def test_async_download_404(self, http_server, download_dir):
        """Test async download with 404 error."""
        import asyncio
        from apt_offline_core.AptOfflineCoreLib import _download_from_web_async
        
        url = f'{http_server["base_url"]}/nonexistent_file.txt'
        local_file = 'should_not_exist.txt'
        
        progress_callback = {
            'addItem': lambda x: None,
            'updateValue': lambda x: None,
            'completed': lambda: None,
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _download_from_web_async(url, local_file, download_dir, progress_callback)
            )
        finally:
            loop.close()
        
        assert result is False
    
    @pytest.mark.skipif(not ASYNC_AVAILABLE, reason='aiohttp/aiofiles not available')
    def test_async_download_progress_callbacks(self, http_server, download_dir):
        """Test that progress callbacks are invoked during async download."""
        import asyncio
        from apt_offline_core.AptOfflineCoreLib import _download_from_web_async
        
        url = f'{http_server["base_url"]}/large_file.bin'
        local_file = 'async_progress.bin'
        
        progress_data = {'items': [], 'bytes': 0, 'completed': 0}
        progress_callback = {
            'addItem': lambda x: progress_data['items'].append(x),
            'updateValue': lambda x: progress_data.update({'bytes': progress_data['bytes'] + x}),
            'completed': lambda: progress_data.update({'completed': progress_data['completed'] + 1}),
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _download_from_web_async(url, local_file, download_dir, progress_callback)
            )
        finally:
            loop.close()
        
        assert result is True
        assert len(progress_data['items']) > 0
        assert progress_data['bytes'] > 0
        assert progress_data['completed'] == 1


class TestDownloadFromWebWrapper:
    """Tests for the download_from_web compatibility wrapper."""
    
    def test_wrapper_with_sync_mode(self, http_server, download_dir):
        """Test wrapper explicitly using sync mode."""
        url = f'{http_server["base_url"]}/test_file.txt'
        local_file = 'wrapper_sync.txt'
        downloader = MockDownloader()
        
        result = download_from_web(downloader, url, local_file, download_dir, use_async=False)
        
        assert result is True
        downloaded_path = os.path.join(download_dir, local_file)
        assert os.path.exists(downloaded_path)
    
    @pytest.mark.skipif(not ASYNC_AVAILABLE, reason='aiohttp/aiofiles not available')
    def test_wrapper_with_async_mode(self, http_server, download_dir):
        """Test wrapper explicitly using async mode."""
        url = f'{http_server["base_url"]}/test_file.txt'
        local_file = 'wrapper_async.txt'
        downloader = MockDownloader()
        
        result = download_from_web(downloader, url, local_file, download_dir, use_async=True)
        
        assert result is True
        downloaded_path = os.path.join(download_dir, local_file)
        assert os.path.exists(downloaded_path)
    
    def test_wrapper_auto_mode(self, http_server, download_dir):
        """Test wrapper with auto-detection (None)."""
        url = f'{http_server["base_url"]}/test_file.txt'
        local_file = 'wrapper_auto.txt'
        downloader = MockDownloader()
        
        result = download_from_web(downloader, url, local_file, download_dir, use_async=None)
        
        assert result is True
        downloaded_path = os.path.join(download_dir, local_file)
        assert os.path.exists(downloaded_path)


class TestAsyncAvailability:
    """Tests for async dependency detection."""
    
    def test_async_available_flag(self):
        """Test that ASYNC_AVAILABLE flag is correctly set."""
        try:
            import aiohttp
            import aiofiles
            assert ASYNC_AVAILABLE is True
        except ImportError:
            assert ASYNC_AVAILABLE is False
    
    def test_wrapper_fallback_when_async_requested_but_unavailable(self, http_server, download_dir):
        """Test that wrapper falls back to sync when async requested but unavailable."""
        # This test always works - if async is unavailable, it falls back
        # If async is available, it uses async (which also works)
        url = f'{http_server["base_url"]}/test_file.txt'
        local_file = 'fallback_test.txt'
        downloader = MockDownloader()
        
        # This should work regardless of ASYNC_AVAILABLE
        result = download_from_web(downloader, url, local_file, download_dir, use_async=True)
        
        # Should succeed either way (async if available, sync as fallback)
        assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
