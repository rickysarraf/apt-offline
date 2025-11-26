#!/usr/bin/env python3
"""Benchmark script for apt-offline download functionality.

This script measures download performance for sync vs async modes.
It runs a local HTTP server to serve generated test files.

Usage:
    python tools/benchmark_download.py --mode sync --concurrency 4
    python tools/benchmark_download.py --mode async --concurrency 4
"""

import argparse
import http.server
import os
import shutil
import socketserver
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path to import apt_offline_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apt_offline_core.AptOfflineCoreLib import (
    ASYNC_AVAILABLE,
    download_from_web,
    _download_from_web_sync,
    GenericDownloadFunction,
)
from apt_offline_core import AptOfflineLib


# Test file sizes
FILE_SIZES = {
    'small': 100 * 1024,       # 100 KB
    'medium': 2 * 1024 * 1024,  # 2 MB
    'large': 10 * 1024 * 1024,  # 10 MB
}


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses logging and serves from a specific directory."""
    
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def create_test_files(directory):
    """Create test files of various sizes."""
    files = {}
    for name, size in FILE_SIZES.items():
        filepath = os.path.join(directory, f'test_{name}.bin')
        with open(filepath, 'wb') as f:
            # Write random-ish data in chunks
            chunk_size = 8192
            written = 0
            while written < size:
                to_write = min(chunk_size, size - written)
                f.write(os.urandom(to_write))
                written += to_write
        files[name] = filepath
    return files


def start_http_server(directory, port=0):
    """Start a local HTTP server serving files from directory.
    
    Returns (server, port, thread).
    """
    import functools
    handler = functools.partial(QuietHTTPRequestHandler, directory=directory)
    server = socketserver.TCPServer(('127.0.0.1', port), handler)
    actual_port = server.server_address[1]
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    return server, actual_port, thread


class BenchmarkProgressBar(AptOfflineLib.ProgressBar):
    """Progress bar for benchmarking that inherits from AptOfflineLib.ProgressBar."""
    
    def __init__(self):
        super().__init__(width=80, total_items=1)
    
    def display(self):
        # Override to suppress output during benchmarks
        pass


class BenchmarkDownloader(BenchmarkProgressBar, GenericDownloadFunction):
    """Downloader that inherits from ProgressBar and GenericDownloadFunction for sync benchmarking."""
    
    def __init__(self):
        super().__init__()


def run_sync_benchmark(url_base, file_names, download_dir, concurrency):
    """Run sync download benchmark using ThreadPoolExecutor."""
    results = {'success': 0, 'failure': 0, 'errors': []}
    
    def download_task(file_name):
        url = f'{url_base}/{file_name}'
        local_file = file_name
        downloader = BenchmarkDownloader()
        
        try:
            success = _download_from_web_sync(downloader, url, local_file, download_dir)
            return success, None
        except Exception as e:
            return False, str(e)
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(download_task, fn): fn for fn in file_names}
        for future in as_completed(futures):
            file_name = futures[future]
            try:
                success, error = future.result()
                if success:
                    results['success'] += 1
                else:
                    results['failure'] += 1
                    if error:
                        results['errors'].append(f'{file_name}: {error}')
            except Exception as e:
                results['failure'] += 1
                results['errors'].append(f'{file_name}: {str(e)}')
    
    elapsed = time.time() - start_time
    return elapsed, results


def run_async_benchmark(url_base, file_names, download_dir, concurrency):
    """Run async download benchmark using asyncio.gather."""
    if not ASYNC_AVAILABLE:
        return None, {'error': 'Async dependencies not available'}
    
    import asyncio
    from apt_offline_core.AptOfflineCoreLib import _download_from_web_async
    
    results = {'success': 0, 'failure': 0, 'errors': []}
    
    async def download_all():
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        async def download_task(file_name):
            async with semaphore:
                url = f'{url_base}/{file_name}'
                local_file = file_name
                progress_callback = {
                    'addItem': lambda x: None,
                    'updateValue': lambda x: None,
                    'completed': lambda: None,
                }
                
                try:
                    success = await _download_from_web_async(
                        url, local_file, download_dir, progress_callback
                    )
                    return success, None
                except Exception as e:
                    return False, str(e)
        
        tasks = [download_task(fn) for fn in file_names]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    start_time = time.time()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        task_results = loop.run_until_complete(download_all())
    finally:
        loop.close()
    
    elapsed = time.time() - start_time
    
    for i, result in enumerate(task_results):
        if isinstance(result, Exception):
            results['failure'] += 1
            results['errors'].append(f'{file_names[i]}: {str(result)}')
        else:
            success, error = result
            if success:
                results['success'] += 1
            else:
                results['failure'] += 1
                if error:
                    results['errors'].append(f'{file_names[i]}: {error}')
    
    return elapsed, results


def main():
    parser = argparse.ArgumentParser(
        description='Benchmark apt-offline download functionality'
    )
    parser.add_argument(
        '--mode',
        choices=['sync', 'async', 'both'],
        default='both',
        help='Download mode to benchmark (default: both)'
    )
    parser.add_argument(
        '--concurrency',
        type=int,
        default=4,
        help='Number of concurrent downloads (default: 4)'
    )
    parser.add_argument(
        '--file-size',
        choices=['small', 'medium', 'large', 'all'],
        default='all',
        help='File size to test (default: all)'
    )
    parser.add_argument(
        '--repeat',
        type=int,
        default=1,
        help='Number of times to repeat each download (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Create temp directories
    serve_dir = tempfile.mkdtemp(prefix='apt-offline-bench-serve-')
    download_dir = tempfile.mkdtemp(prefix='apt-offline-bench-download-')
    
    try:
        # Create test files
        print(f'Creating test files in {serve_dir}...')
        test_files = create_test_files(serve_dir)
        
        # Start HTTP server
        print('Starting local HTTP server...')
        server, port, thread = start_http_server(serve_dir)
        url_base = f'http://127.0.0.1:{port}'
        print(f'Server running at {url_base}')
        
        # Determine which file sizes to test
        if args.file_size == 'all':
            sizes_to_test = ['small', 'medium', 'large']
        else:
            sizes_to_test = [args.file_size]
        
        # Build list of files to download
        file_names = []
        for size in sizes_to_test:
            for i in range(args.repeat):
                file_names.append(f'test_{size}.bin')
        
        print(f'\nBenchmark configuration:')
        print(f'  Concurrency: {args.concurrency}')
        print(f'  File sizes: {sizes_to_test}')
        print(f'  Repeat: {args.repeat}')
        print(f'  Total downloads: {len(file_names)}')
        print()
        
        # Run benchmarks
        if args.mode in ['sync', 'both']:
            print('Running SYNC benchmark...')
            # Clean download directory
            for f in os.listdir(download_dir):
                os.unlink(os.path.join(download_dir, f))
            
            elapsed, results = run_sync_benchmark(
                url_base, file_names, download_dir, args.concurrency
            )
            
            print(f'  Elapsed time: {elapsed:.2f}s')
            print(f'  Success: {results["success"]}/{len(file_names)}')
            print(f'  Failure: {results["failure"]}/{len(file_names)}')
            if results['errors']:
                print(f'  Errors: {results["errors"][:3]}...')
            print()
        
        if args.mode in ['async', 'both']:
            if not ASYNC_AVAILABLE:
                print('ASYNC benchmark skipped: aiohttp/aiofiles not available')
                print('Install with: pip install -r requirements-optional.txt')
            else:
                print('Running ASYNC benchmark...')
                # Clean download directory
                for f in os.listdir(download_dir):
                    os.unlink(os.path.join(download_dir, f))
                
                elapsed, results = run_async_benchmark(
                    url_base, file_names, download_dir, args.concurrency
                )
                
                if elapsed is not None:
                    print(f'  Elapsed time: {elapsed:.2f}s')
                    print(f'  Success: {results["success"]}/{len(file_names)}')
                    print(f'  Failure: {results["failure"]}/{len(file_names)}')
                    if results.get('errors'):
                        print(f'  Errors: {results["errors"][:3]}...')
                else:
                    print(f'  Error: {results.get("error", "Unknown error")}')
            print()
        
        # Shutdown server
        print('Shutting down server...')
        server.shutdown()
        
    finally:
        # Cleanup
        shutil.rmtree(serve_dir, ignore_errors=True)
        shutil.rmtree(download_dir, ignore_errors=True)
    
    print('Benchmark complete.')


if __name__ == '__main__':
    main()
