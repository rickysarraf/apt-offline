# Async Download Mode

apt-offline supports an optional async download mode that uses `aiohttp` and `aiofiles` for non-blocking network and file I/O operations. This can improve download performance, especially when downloading multiple files concurrently.

## Installation

To enable async download mode, install the optional dependencies:

```bash
pip install -r requirements-optional.txt
```

Or install the packages directly:

```bash
pip install aiohttp>=3.8,<4 aiofiles>=23.1,<24
```

## Usage

Once the optional dependencies are installed, apt-offline will automatically use async downloads when available. The async mode is transparent and maintains full backward compatibility with the existing API.

The async download mode:
- Streams downloads in chunks for memory efficiency
- Uses non-blocking file writes with `aiofiles`
- Respects existing progress reporting and GUI termination signals
- Falls back to synchronous downloads if async dependencies are not available

## Benchmark

A benchmark script is provided to compare sync vs async download performance:

```bash
# Run sync mode benchmark
python tools/benchmark_download.py --mode sync --concurrency 4

# Run async mode benchmark  
python tools/benchmark_download.py --mode async --concurrency 4
```

The benchmark script:
- Starts a local HTTP server to serve test files (small ~100KB, medium ~2MB, large ~10MB)
- Downloads files using the specified mode and concurrency level
- Measures wall-clock time and success/failure counts
- Prints a summary of results

Note: The async mode requires the optional dependencies to be installed. If they are not available, the benchmark will skip async mode tests.

## Compatibility

The async download implementation:
- Maintains the same function signatures and return values
- Preserves working-directory behavior
- Respects `guiTerminateSignal` for GUI cancellation
- Reports progress through the same `addItem`, `updateValue`, and `completed` callbacks
- Cleans up partial files on errors

If the optional dependencies are not installed, apt-offline will automatically fall back to the original synchronous download implementation.
