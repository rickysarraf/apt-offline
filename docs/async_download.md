# Async Download Support

apt-offline supports an optional asynchronous download mode using `aiohttp` and `aiofiles` for improved download performance, especially when fetching multiple packages concurrently over real network connections with latency.

## Installing Optional Dependencies

To enable async downloads, install the optional dependencies:

```bash
pip install -r requirements-optional.txt
```

Or install them directly:

```bash
pip install aiohttp aiofiles
```

## How It Works

When `aiohttp` and `aiofiles` are installed, apt-offline will automatically use the async download path for fetching packages. This provides:

- **Non-blocking network IO**: Downloads don't block each other, improving throughput
- **Non-blocking file writes**: Uses `aiofiles` for asynchronous file operations
- **Automatic fallback**: If async libraries are not installed or encounter issues, apt-offline seamlessly falls back to synchronous downloads

No code changes or configuration are required - simply install the dependencies and apt-offline will use the faster async path automatically.

## Performance Considerations

The async download path provides the most benefit when:

- **Downloading over real networks with latency**: The async approach hides network latency by overlapping I/O operations
- **Fetching many small files**: Concurrent downloads reduce total wall-clock time
- **Using slow or congested network connections**: Non-blocking I/O prevents one slow download from blocking others

In local or low-latency scenarios (such as localhost testing), the synchronous threaded approach may actually be faster due to reduced async overhead.

## Verifying Async Mode

You can verify whether async mode is active by running apt-offline with the `--verbose` flag. If async mode encounters issues, you'll see messages about falling back to sync mode.

## Benchmark Script

A benchmark script is provided to compare sync and async download performance:

```bash
# Run from the repository root
python tools/benchmark_download.py

# Specify concurrency level
python tools/benchmark_download.py --concurrency 8

# Run only sync mode
python tools/benchmark_download.py --mode sync

# Run only async mode
python tools/benchmark_download.py --mode async
```

The benchmark script:
1. Spins up a local HTTP server serving test files of various sizes
2. Downloads files using both sync (ThreadPoolExecutor) and async (aiohttp) modes
3. Reports elapsed time and success counts for comparison

### Sample Output (Local Testing)

```
Async Download Benchmark
========================
Server: http://localhost:8765

File sizes:
  small: 100 KB
  medium: 2048 KB
  large: 10240 KB

Running sync benchmark (ThreadPoolExecutor)...
Sync mode: 9 downloads in 0.19s (all succeeded)

Running async benchmark (aiohttp + aiofiles)...
Async mode: 9 downloads in 0.92s (all succeeded)

Summary:
  Sync is 79% faster than async
```

**Note**: In local testing, sync may appear faster due to lack of network latency. The async approach provides benefits with real network connections where latency and congestion are factors.

## Compatibility

- Python 3.7+ (for native asyncio.run support)
- aiohttp >= 3.8
- aiofiles >= 0.8

When the optional dependencies are not installed, apt-offline continues to work exactly as before using synchronous downloads.
