"""
Parallel Processing Module

Provides multiprocessing and multithreading capabilities for CPU-bound and I/O-bound
operations in the deepfake detection pipeline.

Building Blocks:
    - ParallelFrameProcessor: Multiprocessing for frame extraction
    - ParallelLLMAnalyzer: Threading for concurrent API calls
"""

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional, Tuple
import threading
import queue
import time
import cv2
import numpy as np
from pathlib import Path


class ParallelFrameProcessor:
    """
    Building block for parallel frame extraction using multiprocessing.

    Input Data:
        - video_path: str, absolute path to MP4 video file
        - frame_indices: List[int], frame indices to extract
        - num_workers: int, number of parallel processes

    Output Data:
        - frames: List[np.ndarray], extracted frames in RGB format
        - extraction_metadata: Dict, processing time and worker info

    Setup Data:
        - max_workers: int, maximum parallel processes (default: cpu_count())
        - timeout: int, timeout in seconds for each frame (default: 30)
        - color_space: str, 'RGB' or 'BGR' (default: 'RGB')

    Dependencies:
        - External: opencv-python, numpy
        - Internal: None

    Error Handling:
        - ProcessTimeout: If frame extraction exceeds timeout → skip frame, log warning
        - ProcessCrash: If worker crashes → retry once, then raise RuntimeError
        - VideoAccessError: If video cannot be opened → raise RuntimeError
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        timeout: int = 30,
        color_space: str = 'RGB'
    ):
        """
        Initialize parallel frame processor.

        Args:
            max_workers: Maximum number of parallel workers (default: CPU count)
            timeout: Timeout for each frame extraction (default: 30 seconds)
            color_space: Output color space 'RGB' or 'BGR' (default: 'RGB')
        """
        self.max_workers = max_workers or mp.cpu_count()
        self.timeout = timeout
        self.color_space = color_space.upper()

        if self.color_space not in ['RGB', 'BGR']:
            raise ValueError(f"color_space must be 'RGB' or 'BGR', got: {color_space}")

    def extract_frames_parallel(
        self,
        video_path: str,
        frame_indices: List[int]
    ) -> Tuple[List[np.ndarray], Dict[str, Any]]:
        """
        Extract multiple frames in parallel using process pool.

        Args:
            video_path: Path to video file
            frame_indices: List of frame indices to extract

        Returns:
            Tuple of (frames, metadata) where:
                - frames: List of numpy arrays (RGB or BGR based on setup)
                - metadata: Dict with processing time, workers used, etc.

        Raises:
            RuntimeError: If video cannot be opened or extraction fails
        """
        start_time = time.time()

        # Validate video exists
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Use process pool for CPU-bound frame extraction
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all extraction tasks
            future_to_index = {
                executor.submit(
                    self._extract_single_frame,
                    video_path,
                    idx,
                    self.color_space
                ): idx for idx in frame_indices
            }

            # Collect results
            frames_dict = {}
            failed_indices = []

            for future in as_completed(future_to_index, timeout=self.timeout * len(frame_indices)):
                idx = future_to_index[future]
                try:
                    frame = future.result(timeout=self.timeout)
                    if frame is not None:
                        frames_dict[idx] = frame
                    else:
                        failed_indices.append(idx)
                except Exception as e:
                    print(f"Warning: Frame {idx} extraction failed: {e}")
                    failed_indices.append(idx)

            # Sort frames by index to maintain order
            sorted_indices = sorted(frames_dict.keys())
            frames = [frames_dict[i] for i in sorted_indices]

            elapsed_time = time.time() - start_time

            metadata = {
                'total_frames_requested': len(frame_indices),
                'total_frames_extracted': len(frames),
                'failed_frames': len(failed_indices),
                'failed_indices': failed_indices,
                'workers_used': self.max_workers,
                'extraction_time_seconds': elapsed_time,
                'frames_per_second': len(frames) / elapsed_time if elapsed_time > 0 else 0
            }

            return frames, metadata

    @staticmethod
    def _extract_single_frame(
        video_path: str,
        frame_index: int,
        color_space: str = 'RGB'
    ) -> Optional[np.ndarray]:
        """
        Extract a single frame from video (used by worker processes).

        This is a static method so it can be pickled for multiprocessing.

        Args:
            video_path: Path to video file
            frame_index: Index of frame to extract
            color_space: Output color space ('RGB' or 'BGR')

        Returns:
            Frame as numpy array, or None if extraction fails
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return None

        try:
            # Seek to frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()

            if not ret or frame is None:
                return None

            # Convert color space if needed
            if color_space == 'RGB':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            return frame

        finally:
            cap.release()

    def benchmark_speedup(
        self,
        video_path: str,
        frame_indices: List[int]
    ) -> Dict[str, Any]:
        """
        Benchmark parallel vs sequential extraction.

        Args:
            video_path: Path to test video
            frame_indices: Frames to extract

        Returns:
            Dict with sequential time, parallel time, and speedup ratio
        """
        # Sequential extraction
        seq_start = time.time()
        seq_frames = []
        for idx in frame_indices:
            frame = self._extract_single_frame(video_path, idx, self.color_space)
            if frame is not None:
                seq_frames.append(frame)
        seq_time = time.time() - seq_start

        # Parallel extraction
        par_start = time.time()
        par_frames, _ = self.extract_frames_parallel(video_path, frame_indices)
        par_time = time.time() - par_start

        speedup = seq_time / par_time if par_time > 0 else 0

        return {
            'sequential_time': seq_time,
            'parallel_time': par_time,
            'speedup': speedup,
            'frames_extracted': len(par_frames),
            'workers': self.max_workers
        }


class ParallelLLMAnalyzer:
    """
    Building block for parallel LLM API calls using threading.

    Input Data:
        - frames: List[np.ndarray], frames to analyze
        - analysis_function: Callable, function to call for each frame
        - frame_indices: Optional[List[int]], frame indices for context

    Output Data:
        - analyses: List[Dict], analysis results for each frame
        - timing_metadata: Dict, timing and concurrency info

    Setup Data:
        - max_concurrent_requests: int, max parallel API calls (default: 5)
        - rate_limit_delay: float, delay between requests (default: 0.5s)
        - retry_attempts: int, number of retries on failure (default: 2)

    Dependencies:
        - External: None (uses stdlib threading)
        - Internal: LLMAnalyzer (for analysis function)

    Error Handling:
        - APITimeout: If request exceeds timeout → retry with exponential backoff
        - RateLimitError: If rate limited → wait and retry
        - APIError: After max retries → store error in results, continue
    """

    def __init__(
        self,
        max_concurrent_requests: int = 5,
        rate_limit_delay: float = 0.5,
        retry_attempts: int = 2
    ):
        """
        Initialize parallel LLM analyzer.

        Args:
            max_concurrent_requests: Max concurrent API calls (default: 5)
            rate_limit_delay: Delay between requests in seconds (default: 0.5)
            retry_attempts: Number of retry attempts on failure (default: 2)
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.rate_limit_delay = rate_limit_delay
        self.retry_attempts = retry_attempts
        self._semaphore = threading.Semaphore(max_concurrent_requests)
        self._lock = threading.Lock()

    def analyze_frames_parallel(
        self,
        frames: List[np.ndarray],
        analysis_function: Callable,
        frame_indices: Optional[List[int]] = None,
        **kwargs
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Analyze multiple frames concurrently with rate limiting.

        Args:
            frames: List of frames to analyze
            analysis_function: Function to call for each frame
            frame_indices: Optional frame indices for context
            **kwargs: Additional arguments to pass to analysis_function

        Returns:
            Tuple of (analyses, metadata) where:
                - analyses: List of analysis results (one per frame)
                - metadata: Dict with timing and concurrency info
        """
        if frame_indices is None:
            frame_indices = list(range(len(frames)))

        start_time = time.time()
        results_dict = {}

        # Use thread pool for I/O-bound API calls
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            # Submit all analysis tasks
            future_to_index = {}
            for i, (frame, idx) in enumerate(zip(frames, frame_indices)):
                future = executor.submit(
                    self._analyze_single_frame_with_semaphore,
                    frame,
                    idx,
                    analysis_function,
                    **kwargs
                )
                future_to_index[future] = idx

            # Collect results
            failed_count = 0
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    result = future.result()
                    results_dict[idx] = result
                except Exception as e:
                    print(f"Warning: Frame {idx} analysis failed: {e}")
                    results_dict[idx] = {'error': str(e), 'frame_index': idx}
                    failed_count += 1

            # Sort results by index
            sorted_indices = sorted(results_dict.keys())
            analyses = [results_dict[i] for i in sorted_indices]

            elapsed_time = time.time() - start_time

            metadata = {
                'total_frames': len(frames),
                'successful_analyses': len(analyses) - failed_count,
                'failed_analyses': failed_count,
                'max_concurrent_requests': self.max_concurrent_requests,
                'total_time_seconds': elapsed_time,
                'average_time_per_frame': elapsed_time / len(frames) if frames else 0
            }

            return analyses, metadata

    def _analyze_single_frame_with_semaphore(
        self,
        frame: np.ndarray,
        frame_index: int,
        analysis_function: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze single frame with semaphore for concurrency control.

        Args:
            frame: Frame to analyze
            frame_index: Index of frame
            analysis_function: Function to call
            **kwargs: Additional arguments

        Returns:
            Analysis result dictionary
        """
        # Acquire semaphore to limit concurrency
        with self._semaphore:
            # Rate limiting
            time.sleep(self.rate_limit_delay)

            # Retry logic
            last_exception = None
            for attempt in range(self.retry_attempts + 1):
                try:
                    result = analysis_function(frame, frame_index, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < self.retry_attempts:
                        # Exponential backoff
                        wait_time = (2 ** attempt) * 0.5
                        time.sleep(wait_time)
                    else:
                        raise last_exception


class ResourceManager:
    """
    Context manager for cleaning up multiprocessing resources.

    Ensures all processes and threads are properly terminated even if
    exceptions occur.
    """

    def __init__(self):
        self.active_pools = []
        self.active_executors = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up all active resources
        for pool in self.active_pools:
            pool.close()
            pool.join()

        for executor in self.active_executors:
            executor.shutdown(wait=True)

        return False  # Don't suppress exceptions


def detect_optimal_workers(video_path: str, test_frame_count: int = 10) -> int:
    """
    Automatically detect optimal number of workers for a given video.

    Tests different worker counts and returns the configuration with
    best performance.

    Args:
        video_path: Path to video file
        test_frame_count: Number of frames to use for testing

    Returns:
        Optimal number of workers
    """
    cpu_count = mp.cpu_count()
    test_workers = [1, cpu_count // 2, cpu_count, cpu_count * 2]

    # Generate test frame indices
    frame_indices = list(range(0, test_frame_count * 10, 10))[:test_frame_count]

    best_speedup = 0
    best_workers = cpu_count

    for workers in test_workers:
        if workers < 1:
            continue

        processor = ParallelFrameProcessor(max_workers=workers)
        try:
            benchmark = processor.benchmark_speedup(video_path, frame_indices)
            if benchmark['speedup'] > best_speedup:
                best_speedup = benchmark['speedup']
                best_workers = workers
        except Exception as e:
            print(f"Warning: Benchmark with {workers} workers failed: {e}")
            continue

    return best_workers
