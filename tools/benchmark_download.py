#!/usr/bin/env python3
"""
Benchmark script for comparing sync vs async download performance.

This script can perform n parallel downloads using both the sync and async paths
to measure throughput and wall-clock time.

Usage:
    python benchmark_download.py --urls URL1 URL2 ... --repeat N --concurrency M
    python benchmark_download.py --url URL --repeat N --concurrency M

Examples:
    # Test with a single URL repeated 5 times, 3 concurrent downloads
    python benchmark_download.py --url https://example.com/file.txt --repeat 5 --concurrency 3

    # Test with multiple URLs
    python benchmark_download.py --urls https://example.com/a.txt https://example.com/b.txt --repeat 2
"""

import argparse
import asyncio
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apt_offline_core.AptOfflineCoreLib import (
    AIOHTTP_AVAILABLE,
    GenericDownloadFunction,
)
from apt_offline_core import AptOfflineLib


class BenchmarkDownloader(AptOfflineLib.ProgressBar, GenericDownloadFunction):
    """A minimal downloader class for benchmarking purposes."""

    def __init__(self):
        AptOfflineLib.ProgressBar.__init__(self, width=50, total_items=0)

    def display(self):
        """Suppress progress display during benchmarks."""
        pass


def run_sync_benchmark(urls, download_dir, concurrency):
    """
    Run sync downloads using ThreadPoolExecutor to simulate prior threading model.

    Returns (elapsed_time, success_count, failure_count)
    """
    success_count = 0
    failure_count = 0

    def download_single(url_info):
        url, index = url_info
        downloader = BenchmarkDownloader()
        filename = f"sync_download_{index}.tmp"
        try:
            result = downloader._download_from_web_sync(url, filename, download_dir)
            # Clean up the downloaded file
            filepath = os.path.join(download_dir, filename)
            if os.path.exists(filepath):
                os.unlink(filepath)
            return result
        except Exception as e:
            print(f"Sync download error for {url}: {e}")
            return False

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(download_single, (url, i)): url
            for i, url in enumerate(urls)
        }
        for future in as_completed(futures):
            if future.result():
                success_count += 1
            else:
                failure_count += 1

    elapsed_time = time.time() - start_time
    return elapsed_time, success_count, failure_count


async def download_async_single(url, index, download_dir):
    """Download a single file asynchronously."""
    downloader = BenchmarkDownloader()
    filename = f"async_download_{index}.tmp"
    try:
        result = await downloader._download_from_web_async(url, filename, download_dir)
        # Clean up the downloaded file
        filepath = os.path.join(download_dir, filename)
        if os.path.exists(filepath):
            os.unlink(filepath)
        return result
    except Exception as e:
        print(f"Async download error for {url}: {e}")
        return False


async def run_async_downloads(urls, download_dir, concurrency):
    """Run async downloads with semaphore-based concurrency control."""
    semaphore = asyncio.Semaphore(concurrency)
    success_count = 0
    failure_count = 0

    async def bounded_download(url, index):
        async with semaphore:
            return await download_async_single(url, index, download_dir)

    tasks = [bounded_download(url, i) for i, url in enumerate(urls)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            failure_count += 1
        elif result:
            success_count += 1
        else:
            failure_count += 1

    return success_count, failure_count


def run_async_benchmark(urls, download_dir, concurrency):
    """
    Run async downloads using asyncio.

    Returns (elapsed_time, success_count, failure_count)
    """
    if not AIOHTTP_AVAILABLE:
        print("aiohttp is not available. Cannot run async benchmark.")
        return None, 0, len(urls)

    start_time = time.time()
    success_count, failure_count = asyncio.run(
        run_async_downloads(urls, download_dir, concurrency)
    )
    elapsed_time = time.time() - start_time

    return elapsed_time, success_count, failure_count


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark sync vs async download performance"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Single URL to download (will be repeated based on --repeat)",
    )
    parser.add_argument(
        "--urls", type=str, nargs="+", help="List of URLs to download"
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat each URL (default: 1)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent downloads (default: 5)",
    )
    parser.add_argument(
        "--sync-only",
        action="store_true",
        help="Run only the sync benchmark",
    )
    parser.add_argument(
        "--async-only",
        action="store_true",
        help="Run only the async benchmark",
    )

    args = parser.parse_args()

    # Validate URL arguments
    if not args.url and not args.urls:
        parser.error("Either --url or --urls must be provided")

    # Build URL list
    if args.url:
        urls = [args.url] * args.repeat
    else:
        urls = args.urls * args.repeat

    print(f"Benchmark Configuration:")
    print(f"  Total downloads: {len(urls)}")
    print(f"  Concurrency: {args.concurrency}")
    print(f"  aiohttp available: {AIOHTTP_AVAILABLE}")
    print()

    # Create temporary download directory
    with tempfile.TemporaryDirectory() as download_dir:
        print(f"Download directory: {download_dir}")
        print()

        results = {}

        # Run sync benchmark
        if not args.async_only:
            print("Running SYNC benchmark...")
            sync_time, sync_success, sync_failure = run_sync_benchmark(
                urls, download_dir, args.concurrency
            )
            results["sync"] = {
                "time": sync_time,
                "success": sync_success,
                "failure": sync_failure,
            }
            print(f"  Elapsed time: {sync_time:.2f}s")
            print(f"  Success: {sync_success}, Failure: {sync_failure}")
            print()

        # Run async benchmark
        if not args.sync_only:
            print("Running ASYNC benchmark...")
            async_time, async_success, async_failure = run_async_benchmark(
                urls, download_dir, args.concurrency
            )
            if async_time is not None:
                results["async"] = {
                    "time": async_time,
                    "success": async_success,
                    "failure": async_failure,
                }
                print(f"  Elapsed time: {async_time:.2f}s")
                print(f"  Success: {async_success}, Failure: {async_failure}")
            else:
                print("  Skipped (aiohttp not available)")
            print()

        # Summary
        print("=" * 50)
        print("SUMMARY")
        print("=" * 50)
        for mode, data in results.items():
            throughput = data["success"] / data["time"] if data["time"] > 0 else 0
            print(
                f"{mode.upper():6s}: {data['time']:7.2f}s | "
                f"Success: {data['success']:3d} | "
                f"Failure: {data['failure']:3d} | "
                f"Throughput: {throughput:.2f} downloads/s"
            )

        if "sync" in results and "async" in results:
            speedup = results["sync"]["time"] / results["async"]["time"]
            print()
            print(f"Async speedup: {speedup:.2f}x faster than sync")


if __name__ == "__main__":
    main()
