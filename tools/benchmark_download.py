#!/usr/bin/env python3
"""
Benchmark script for comparing sync and async download performance.

This script:
1. Starts a local HTTP server serving test files of various sizes
2. Downloads files using both sync (ThreadPoolExecutor) and async (aiohttp) modes
3. Reports elapsed time and success counts for comparison

Usage:
    python tools/benchmark_download.py [--mode sync|async|both] [--concurrency N]
"""

import argparse
import asyncio
import http.server
import os
import socketserver
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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


# File sizes for benchmarking (in KB)
FILE_SIZES = {
    'small': 100,      # 100 KB
    'medium': 2048,    # 2 MB
    'large': 10240,    # 10 MB
}


def generate_test_files(directory):
    """Generate test files of various sizes."""
    files = {}
    for name, size_kb in FILE_SIZES.items():
        filepath = os.path.join(directory, f'test_{name}.bin')
        with open(filepath, 'wb') as f:
            # Write random-ish data in chunks
            chunk = b'x' * 1024  # 1 KB chunk
            for _ in range(size_kb):
                f.write(chunk)
        files[name] = filepath
    return files


def start_server(directory, port=0):
    """Start a local HTTP server in a separate thread."""
    original_dir = os.getcwd()
    os.chdir(directory)
    
    # Create handler that serves from fixed directory
    handler = lambda *args, **kwargs: FixedDirectoryHTTPRequestHandler(*args, directory=directory, **kwargs)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    actual_port = httpd.server_address[1]
    
    os.chdir(original_dir)
    
    def serve():
        httpd.serve_forever()
    
    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    return httpd, actual_port


class FixedDirectoryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves from a fixed directory."""
    
    def __init__(self, *args, directory=None, **kwargs):
        self.fixed_directory = directory
        super().__init__(*args, **kwargs)
    
    def translate_path(self, path):
        """Translate URL path to filesystem path, using fixed directory."""
        path = super().translate_path(path)
        relpath = os.path.relpath(path, os.getcwd())
        return os.path.join(self.fixed_directory, relpath)
    
    def log_message(self, format, *args):
        pass


def sync_download(url, dest_path):
    """Synchronous download using urllib."""
    import urllib.request
    try:
        with urllib.request.urlopen(url) as response:
            with open(dest_path, 'wb') as f:
                while True:
                    chunk = response.read(4096)
                    if not chunk:
                        break
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Sync download error: {e}")
        return False


async def async_download(session, url, dest_path):
    """Async download using aiohttp and aiofiles."""
    try:
        async with session.get(url) as response:
            if response.status >= 400:
                return False
            async with aiofiles.open(dest_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(4096):
                    await f.write(chunk)
        return True
    except Exception as e:
        print(f"Async download error: {e}")
        return False


def run_sync_benchmark(urls, download_dir, concurrency):
    """Run sync downloads using ThreadPoolExecutor."""
    successes = 0
    
    def download_task(args):
        url, filename = args
        dest = os.path.join(download_dir, filename)
        return sync_download(url, dest)
    
    tasks = [(url, f"sync_{i}_{os.path.basename(url)}") for i, url in enumerate(urls)]
    
    start = time.time()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        results = list(executor.map(download_task, tasks))
    elapsed = time.time() - start
    
    successes = sum(1 for r in results if r)
    return elapsed, successes, len(urls)


async def run_async_benchmark(urls, download_dir, concurrency):
    """Run async downloads using aiohttp."""
    successes = 0
    
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i, url in enumerate(urls):
            dest = os.path.join(download_dir, f"async_{i}_{os.path.basename(url)}")
            tasks.append(async_download(session, url, dest))
        
        start = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start
    
    successes = sum(1 for r in results if r)
    return elapsed, successes, len(urls)


def main():
    parser = argparse.ArgumentParser(
        description='Benchmark sync vs async download performance'
    )
    parser.add_argument(
        '--mode', 
        choices=['sync', 'async', 'both'],
        default='both',
        help='Benchmark mode (default: both)'
    )
    parser.add_argument(
        '--concurrency',
        type=int,
        default=4,
        help='Number of concurrent downloads (default: 4)'
    )
    parser.add_argument(
        '--downloads-per-size',
        type=int,
        default=3,
        help='Number of downloads per file size (default: 3)'
    )
    args = parser.parse_args()
    
    if args.mode in ('async', 'both') and not ASYNC_AVAILABLE:
        print("ERROR: aiohttp and/or aiofiles not installed.")
        print("Install with: pip install aiohttp aiofiles")
        if args.mode == 'async':
            sys.exit(1)
        print("Running sync benchmark only.\n")
        args.mode = 'sync'
    
    print("Async Download Benchmark")
    print("=" * 50)
    
    # Create temp directories
    with tempfile.TemporaryDirectory() as server_dir:
        with tempfile.TemporaryDirectory() as download_dir:
            # Generate test files
            print("\nGenerating test files...")
            test_files = generate_test_files(server_dir)
            
            # Start server
            print("Starting local HTTP server...")
            httpd, port = start_server(server_dir)
            base_url = f"http://localhost:{port}"
            
            print(f"\nServer: {base_url}")
            print("\nFile sizes:")
            for name, size in FILE_SIZES.items():
                print(f"  {name}: {size} KB")
            
            # Build URL list
            urls = []
            for _ in range(args.downloads_per_size):
                for name in FILE_SIZES.keys():
                    urls.append(f"{base_url}/test_{name}.bin")
            
            total_downloads = len(urls)
            print(f"\nTotal downloads per mode: {total_downloads}")
            print(f"Concurrency: {args.concurrency}")
            
            results = {}
            
            # Run sync benchmark
            if args.mode in ('sync', 'both'):
                print("\nRunning sync benchmark (ThreadPoolExecutor)...")
                elapsed, successes, total = run_sync_benchmark(
                    urls, download_dir, args.concurrency
                )
                results['sync'] = (elapsed, successes, total)
                print(f"Sync mode: {total} downloads in {elapsed:.2f}s ({successes} succeeded)")
                
                # Clean up downloaded files
                for f in os.listdir(download_dir):
                    if f.startswith('sync_'):
                        os.remove(os.path.join(download_dir, f))
            
            # Run async benchmark
            if args.mode in ('async', 'both'):
                print("\nRunning async benchmark (aiohttp + aiofiles)...")
                elapsed, successes, total = asyncio.run(
                    run_async_benchmark(urls, download_dir, args.concurrency)
                )
                results['async'] = (elapsed, successes, total)
                print(f"Async mode: {total} downloads in {elapsed:.2f}s ({successes} succeeded)")
            
            # Print summary
            if args.mode == 'both' and 'sync' in results and 'async' in results:
                print("\n" + "=" * 50)
                print("Summary:")
                sync_time = results['sync'][0]
                async_time = results['async'][0]
                if async_time < sync_time:
                    improvement = ((sync_time - async_time) / sync_time) * 100
                    print(f"  Async is {improvement:.0f}% faster than sync")
                elif sync_time < async_time:
                    slowdown = ((async_time - sync_time) / async_time) * 100
                    print(f"  Sync is {slowdown:.0f}% faster than async")
                else:
                    print("  Performance is similar")
            
            # Shutdown server
            httpd.shutdown()
    
    print("\nBenchmark complete.")


if __name__ == '__main__':
    main()
