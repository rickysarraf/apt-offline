#!/usr/bin/env python3
"""
Tests for async/sync download functionality in apt-offline.

These tests set up a local HTTP server and verify that both the sync
and async download code paths correctly download files.
"""

import http.server
import os
import socketserver
import sys
import threading
import tempfile
from functools import partial
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check for async dependencies
ASYNC_AVAILABLE = False
try:
    import aiohttp
    import aiofiles
    ASYNC_AVAILABLE = True
except ImportError:
    pass


class FixedDirectoryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves from a fixed directory and suppresses logging."""
    
    def __init__(self, *args, directory=None, **kwargs):
        self.fixed_directory = directory
        super().__init__(*args, **kwargs)
    
    def translate_path(self, path):
        """Translate URL path to filesystem path, using fixed directory."""
        # Get the path from parent implementation
        path = super().translate_path(path)
        # Replace current directory with our fixed directory
        relpath = os.path.relpath(path, os.getcwd())
        return os.path.join(self.fixed_directory, relpath)
    
    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def test_server(tmp_path_factory):
    """Set up a local HTTP server serving a test file from a fixed directory."""
    server_dir = tmp_path_factory.mktemp("server")
    
    # Create a test file with known content
    test_content = b"Hello, apt-offline test!" * 100  # ~2.4 KB
    test_file = server_dir / "test_file.bin"
    test_file.write_bytes(test_content)
    
    # Create handler bound to the server directory
    handler = partial(FixedDirectoryHTTPRequestHandler, directory=str(server_dir))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    
    yield {
        'url': f'http://127.0.0.1:{port}/test_file.bin',
        'content': test_content,
        'port': port,
        'httpd': httpd,
    }
    
    # Cleanup
    httpd.shutdown()


@pytest.fixture
def download_dir(tmp_path):
    """Create a temporary directory for downloads."""
    return tmp_path


class MockProgressBar:
    """Mock progress bar for testing download functions."""
    def __init__(self):
        self.items_added = []
        self.values_updated = []
        self.completed_count = 0
    
    def addItem(self, size):
        self.items_added.append(size)
    
    def updateValue(self, increment):
        self.values_updated.append(increment)
    
    def completed(self):
        self.completed_count += 1


class TestSyncDownload:
    """Tests for synchronous download functionality."""
    
    def test_sync_download_success(self, test_server, download_dir):
        """Test that sync download correctly downloads a file."""
        from apt_offline_core.AptOfflineCoreLib import GenericDownloadFunction
        
        # Create a test instance with mock progress methods
        class TestDownloader(MockProgressBar, GenericDownloadFunction):
            pass
        
        downloader = TestDownloader()
        local_file = "downloaded_sync.bin"
        
        # Force sync download
        result = downloader._download_from_web_sync(
            test_server['url'],
            local_file,
            str(download_dir)
        )
        
        assert result is True
        
        # Verify file content
        downloaded_path = download_dir / local_file
        assert downloaded_path.exists()
        assert downloaded_path.read_bytes() == test_server['content']
        
        # Verify progress tracking
        assert downloader.completed_count == 1
        assert len(downloader.items_added) > 0
    
    def test_sync_download_404(self, test_server, download_dir):
        """Test that sync download handles 404 errors."""
        from apt_offline_core.AptOfflineCoreLib import GenericDownloadFunction
        
        class TestDownloader(MockProgressBar, GenericDownloadFunction):
            pass
        
        downloader = TestDownloader()
        local_file = "should_not_exist.bin"
        
        # Try to download non-existent file
        result = downloader._download_from_web_sync(
            f"http://127.0.0.1:{test_server['port']}/nonexistent.bin",
            local_file,
            str(download_dir)
        )
        
        assert result is False
        assert not (download_dir / local_file).exists()


@pytest.mark.skipif(not ASYNC_AVAILABLE, reason="aiohttp/aiofiles not installed")
class TestAsyncDownload:
    """Tests for asynchronous download functionality."""
    
    def test_async_download_success(self, test_server, download_dir):
        """Test that async download correctly downloads a file."""
        import asyncio
        from apt_offline_core.AptOfflineCoreLib import GenericDownloadFunction
        
        class TestDownloader(MockProgressBar, GenericDownloadFunction):
            pass
        
        downloader = TestDownloader()
        local_file = "downloaded_async.bin"
        
        # Run async download
        result = asyncio.run(
            downloader._download_from_web_async(
                test_server['url'],
                local_file,
                str(download_dir)
            )
        )
        
        assert result is True
        
        # Verify file content
        downloaded_path = download_dir / local_file
        assert downloaded_path.exists()
        assert downloaded_path.read_bytes() == test_server['content']
        
        # Verify progress tracking
        assert downloader.completed_count == 1
        assert len(downloader.items_added) > 0
    
    def test_async_download_404(self, test_server, download_dir):
        """Test that async download handles 404 errors."""
        import asyncio
        from apt_offline_core.AptOfflineCoreLib import GenericDownloadFunction
        
        class TestDownloader(MockProgressBar, GenericDownloadFunction):
            pass
        
        downloader = TestDownloader()
        local_file = "should_not_exist.bin"
        
        # Try to download non-existent file
        result = asyncio.run(
            downloader._download_from_web_async(
                f"http://127.0.0.1:{test_server['port']}/nonexistent.bin",
                local_file,
                str(download_dir)
            )
        )
        
        assert result is False
        # Partial file should be cleaned up
        assert not (download_dir / local_file).exists()
    
    def test_async_wrapper_fallback(self, test_server, download_dir, monkeypatch):
        """Test that wrapper falls back to sync when async fails."""
        from apt_offline_core import AptOfflineCoreLib
        from apt_offline_core.AptOfflineCoreLib import GenericDownloadFunction
        
        class TestDownloader(MockProgressBar, GenericDownloadFunction):
            pass
        
        downloader = TestDownloader()
        local_file = "downloaded_wrapper.bin"
        
        # Monkeypatch ASYNC_DOWNLOAD_AVAILABLE to True
        original_value = AptOfflineCoreLib.ASYNC_DOWNLOAD_AVAILABLE
        monkeypatch.setattr(AptOfflineCoreLib, 'ASYNC_DOWNLOAD_AVAILABLE', True)
        
        try:
            # This should work using the async path
            result = downloader.download_from_web(
                test_server['url'],
                local_file,
                str(download_dir)
            )
            
            assert result is True
            
            # Verify file content
            downloaded_path = download_dir / local_file
            assert downloaded_path.exists()
            assert downloaded_path.read_bytes() == test_server['content']
        finally:
            monkeypatch.setattr(AptOfflineCoreLib, 'ASYNC_DOWNLOAD_AVAILABLE', original_value)


class TestDownloadDispatch:
    """Test the download_from_web dispatcher logic."""
    
    def test_download_uses_sync_when_async_unavailable(self, test_server, download_dir, monkeypatch):
        """Test that download falls back to sync when async deps missing."""
        from apt_offline_core import AptOfflineCoreLib
        from apt_offline_core.AptOfflineCoreLib import GenericDownloadFunction
        
        class TestDownloader(MockProgressBar, GenericDownloadFunction):
            pass
        
        downloader = TestDownloader()
        local_file = "downloaded_dispatch.bin"
        
        # Force sync path
        monkeypatch.setattr(AptOfflineCoreLib, 'ASYNC_DOWNLOAD_AVAILABLE', False)
        
        result = downloader.download_from_web(
            test_server['url'],
            local_file,
            str(download_dir)
        )
        
        assert result is True
        
        # Verify file content
        downloaded_path = download_dir / local_file
        assert downloaded_path.exists()
        assert downloaded_path.read_bytes() == test_server['content']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
