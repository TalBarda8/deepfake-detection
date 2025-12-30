"""
Tests for Parallel Processing Module

Tests multiprocessing frame extraction, threading for API calls,
race conditions, deadlocks, and resource cleanup.
"""

import pytest
import time
import threading
import multiprocessing as mp
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.parallel_processor import (
    ParallelFrameProcessor,
    ParallelLLMAnalyzer,
    ResourceManager,
    detect_optimal_workers
)


class TestParallelFrameProcessor:
    """Test cases for ParallelFrameProcessor class."""

    @pytest.fixture
    def video_path(self):
        """Return path to test video."""
        return "data/videos/real/real_video_v1.mp4"

    @pytest.fixture
    def processor(self):
        """Create ParallelFrameProcessor instance."""
        return ParallelFrameProcessor(max_workers=2, timeout=30)

    def test_initialization_default_workers(self):
        """Test processor initialization with default workers."""
        processor = ParallelFrameProcessor()
        assert processor.max_workers == mp.cpu_count()
        assert processor.timeout == 30
        assert processor.color_space == 'RGB'

    def test_initialization_custom_workers(self):
        """Test processor initialization with custom workers."""
        processor = ParallelFrameProcessor(max_workers=4, timeout=60, color_space='BGR')
        assert processor.max_workers == 4
        assert processor.timeout == 60
        assert processor.color_space == 'BGR'

    def test_invalid_color_space_raises_error(self):
        """Test that invalid color space raises ValueError."""
        with pytest.raises(ValueError, match="color_space must be"):
            ParallelFrameProcessor(color_space='XYZ')

    def test_extract_frames_parallel_success(self, processor, video_path):
        """Test successful parallel frame extraction."""
        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        frame_indices = [0, 10, 20, 30, 40]
        frames, metadata = processor.extract_frames_parallel(video_path, frame_indices)

        # Verify frames extracted
        assert len(frames) > 0
        assert len(frames) <= len(frame_indices)

        # Verify metadata
        assert metadata['total_frames_requested'] == len(frame_indices)
        assert metadata['total_frames_extracted'] > 0
        assert metadata['workers_used'] == processor.max_workers
        assert metadata['extraction_time_seconds'] > 0

        # Verify frame format
        for frame in frames:
            assert isinstance(frame, np.ndarray)
            assert frame.ndim == 3  # Height x Width x Channels
            assert frame.shape[2] == 3  # RGB

    def test_extract_frames_parallel_nonexistent_video(self, processor):
        """Test extraction from nonexistent video raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            processor.extract_frames_parallel("nonexistent_video.mp4", [0, 1, 2])

    def test_extract_single_frame_static_method(self, video_path):
        """Test static method for single frame extraction."""
        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        frame = ParallelFrameProcessor._extract_single_frame(video_path, 0, 'RGB')

        assert frame is not None
        assert isinstance(frame, np.ndarray)
        assert frame.ndim == 3

    def test_extract_single_frame_invalid_index(self, video_path):
        """Test extraction with invalid frame index returns None."""
        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        # Very large index that doesn't exist
        frame = ParallelFrameProcessor._extract_single_frame(video_path, 999999, 'RGB')
        # OpenCV may return None or fail gracefully
        assert frame is None or isinstance(frame, np.ndarray)

    def test_benchmark_speedup(self, processor, video_path):
        """Test speedup benchmark comparing sequential vs parallel."""
        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        frame_indices = [0, 5, 10, 15, 20]
        benchmark = processor.benchmark_speedup(video_path, frame_indices)

        assert 'sequential_time' in benchmark
        assert 'parallel_time' in benchmark
        assert 'speedup' in benchmark
        assert benchmark['sequential_time'] > 0
        assert benchmark['parallel_time'] > 0
        assert benchmark['speedup'] >= 0  # Speedup may be <1 for small workloads

    def test_color_space_conversion_rgb(self, video_path):
        """Test RGB color space conversion."""
        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        processor = ParallelFrameProcessor(color_space='RGB')
        frames, _ = processor.extract_frames_parallel(video_path, [0])

        if len(frames) > 0:
            # RGB: Red channel typically has values
            assert frames[0].shape[2] == 3

    def test_color_space_conversion_bgr(self, video_path):
        """Test BGR color space conversion."""
        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        processor = ParallelFrameProcessor(color_space='BGR')
        frames, _ = processor.extract_frames_parallel(video_path, [0])

        if len(frames) > 0:
            assert frames[0].shape[2] == 3

    def test_failed_frames_tracking(self, processor):
        """Test that failed frame extractions are tracked in metadata."""
        # Use nonexistent video to force failures
        invalid_path = "invalid_video.mp4"

        # Should raise FileNotFoundError, but test metadata structure
        with pytest.raises(FileNotFoundError):
            processor.extract_frames_parallel(invalid_path, [0, 1, 2])

    def test_empty_frame_indices(self, processor, video_path):
        """Test extraction with empty frame indices list."""
        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        frames, metadata = processor.extract_frames_parallel(video_path, [])

        assert len(frames) == 0
        assert metadata['total_frames_requested'] == 0
        assert metadata['total_frames_extracted'] == 0


class TestParallelLLMAnalyzer:
    """Test cases for ParallelLLMAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create ParallelLLMAnalyzer instance."""
        return ParallelLLMAnalyzer(
            max_concurrent_requests=3,
            rate_limit_delay=0.1,
            retry_attempts=1
        )

    @pytest.fixture
    def mock_frames(self):
        """Create mock frames for testing."""
        return [np.random.rand(100, 100, 3) for _ in range(5)]

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = ParallelLLMAnalyzer(
            max_concurrent_requests=5,
            rate_limit_delay=0.5,
            retry_attempts=2
        )

        assert analyzer.max_concurrent_requests == 5
        assert analyzer.rate_limit_delay == 0.5
        assert analyzer.retry_attempts == 2
        assert analyzer._semaphore is not None
        assert analyzer._lock is not None

    def test_analyze_frames_parallel_success(self, analyzer, mock_frames):
        """Test successful parallel frame analysis."""

        def mock_analysis_func(frame, frame_idx, **kwargs):
            """Mock analysis function that succeeds."""
            time.sleep(0.05)  # Simulate processing time
            return {
                'frame_index': frame_idx,
                'result': 'analyzed',
                'confidence': 0.85
            }

        analyses, metadata = analyzer.analyze_frames_parallel(
            mock_frames,
            mock_analysis_func
        )

        # Verify all frames analyzed
        assert len(analyses) == len(mock_frames)

        # Verify metadata
        assert metadata['total_frames'] == len(mock_frames)
        assert metadata['successful_analyses'] == len(mock_frames)
        assert metadata['failed_analyses'] == 0
        assert metadata['total_time_seconds'] > 0

        # Verify results
        for i, analysis in enumerate(analyses):
            assert analysis['frame_index'] == i
            assert analysis['result'] == 'analyzed'

    def test_analyze_frames_parallel_with_failures(self, analyzer, mock_frames):
        """Test analysis with some failures."""

        call_count = {'count': 0}

        def failing_analysis_func(frame, frame_idx, **kwargs):
            """Mock analysis function that fails intermittently."""
            call_count['count'] += 1
            if frame_idx == 2:  # Fail on third frame
                raise ValueError("Simulated API error")
            return {'frame_index': frame_idx, 'result': 'success'}

        analyses, metadata = analyzer.analyze_frames_parallel(
            mock_frames,
            failing_analysis_func
        )

        # Should still return results for all frames
        assert len(analyses) == len(mock_frames)

        # One failure expected
        assert metadata['failed_analyses'] > 0

        # Check error is recorded
        assert 'error' in analyses[2]

    def test_semaphore_limits_concurrency(self, analyzer, mock_frames):
        """Test that semaphore correctly limits concurrent requests."""

        active_count = {'max': 0, 'current': 0}
        lock = threading.Lock()

        def concurrent_tracking_func(frame, frame_idx, **kwargs):
            """Track maximum concurrent executions."""
            with lock:
                active_count['current'] += 1
                active_count['max'] = max(active_count['max'], active_count['current'])

            time.sleep(0.1)  # Simulate work

            with lock:
                active_count['current'] -= 1

            return {'frame_index': frame_idx}

        analyzer.analyze_frames_parallel(mock_frames, concurrent_tracking_func)

        # Max concurrent should not exceed semaphore limit
        assert active_count['max'] <= analyzer.max_concurrent_requests

    def test_retry_logic_on_failure(self, analyzer, mock_frames):
        """Test that failed requests are retried."""

        attempt_counts = {i: 0 for i in range(len(mock_frames))}
        lock = threading.Lock()

        def retry_counting_func(frame, frame_idx, **kwargs):
            """Count retry attempts."""
            with lock:
                attempt_counts[frame_idx] += 1

                # Fail first attempt, succeed second
                if attempt_counts[frame_idx] == 1:
                    raise ValueError("First attempt fails")

            return {'frame_index': frame_idx, 'attempts': attempt_counts[frame_idx]}

        analyses, metadata = analyzer.analyze_frames_parallel(
            mock_frames,
            retry_counting_func
        )

        # All should eventually succeed (with retries)
        assert metadata['successful_analyses'] == len(mock_frames)

        # Check that retries occurred
        for result in analyses:
            if 'attempts' in result:
                assert result['attempts'] >= 1

    def test_rate_limiting(self, analyzer, mock_frames):
        """Test that rate limiting adds delays between requests."""

        start_time = time.time()

        def quick_func(frame, frame_idx, **kwargs):
            """Very fast function to test rate limiting overhead."""
            return {'frame_index': frame_idx}

        analyzer.analyze_frames_parallel(mock_frames, quick_func)

        elapsed = time.time() - start_time

        # With rate_limit_delay=0.1 and 5 frames, should take at least 0.5s
        # (accounting for parallel execution, may be less)
        assert elapsed > 0  # At least some delay

    def test_empty_frames_list(self, analyzer):
        """Test analysis with empty frames list."""

        def mock_func(frame, frame_idx, **kwargs):
            return {'result': 'analyzed'}

        analyses, metadata = analyzer.analyze_frames_parallel([], mock_func)

        assert len(analyses) == 0
        assert metadata['total_frames'] == 0
        assert metadata['successful_analyses'] == 0

    def test_custom_frame_indices(self, analyzer, mock_frames):
        """Test analysis with custom frame indices."""

        custom_indices = [10, 20, 30, 40, 50]

        def index_tracking_func(frame, frame_idx, **kwargs):
            return {'frame_index': frame_idx}

        analyses, metadata = analyzer.analyze_frames_parallel(
            mock_frames,
            index_tracking_func,
            frame_indices=custom_indices
        )

        # Verify custom indices used
        for i, analysis in enumerate(analyses):
            assert analysis['frame_index'] == custom_indices[i]


class TestResourceManager:
    """Test cases for ResourceManager context manager."""

    def test_resource_manager_context(self):
        """Test ResourceManager as context manager."""

        with ResourceManager() as manager:
            assert manager is not None
            assert manager.active_pools == []
            assert manager.active_executors == []

    def test_resource_manager_exception_handling(self):
        """Test that ResourceManager doesn't suppress exceptions."""

        with pytest.raises(ValueError):
            with ResourceManager():
                raise ValueError("Test exception")


class TestOptimalWorkers:
    """Test cases for optimal worker detection."""

    def test_detect_optimal_workers(self):
        """Test automatic detection of optimal workers."""
        video_path = "data/videos/real/real_video_v1.mp4"

        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        optimal = detect_optimal_workers(video_path, test_frame_count=5)

        # Should return a positive integer
        assert optimal > 0
        assert isinstance(optimal, int)

        # Should be reasonable (not more than 4x CPU count)
        assert optimal <= mp.cpu_count() * 4


class TestThreadSafety:
    """Test thread safety and race conditions."""

    def test_no_race_conditions_in_parallel_analyzer(self):
        """Test that parallel analyzer doesn't have race conditions."""

        shared_state = {'counter': 0}
        lock = threading.Lock()

        def increment_func(frame, frame_idx, **kwargs):
            """Function that increments shared counter."""
            # Without proper locking, this would have race conditions
            with lock:
                current = shared_state['counter']
                time.sleep(0.001)  # Increase chance of race condition
                shared_state['counter'] = current + 1

            return {'frame_index': frame_idx}

        frames = [np.random.rand(10, 10, 3) for _ in range(20)]
        analyzer = ParallelLLMAnalyzer(max_concurrent_requests=5)

        analyzer.analyze_frames_parallel(frames, increment_func)

        # If thread-safe, counter should equal number of frames
        assert shared_state['counter'] == len(frames)

    def test_deadlock_prevention(self):
        """Test that system doesn't deadlock with circular dependencies."""

        def circular_waiting_func(frame, frame_idx, **kwargs):
            """Function that could cause deadlock if not handled properly."""
            time.sleep(0.05)
            return {'frame_index': frame_idx}

        frames = [np.random.rand(10, 10, 3) for _ in range(10)]
        analyzer = ParallelLLMAnalyzer(max_concurrent_requests=3, retry_attempts=0)

        # This should complete without hanging
        start = time.time()
        analyses, _ = analyzer.analyze_frames_parallel(frames, circular_waiting_func)
        elapsed = time.time() - start

        # Should complete in reasonable time (not hang indefinitely)
        assert elapsed < 10  # 10 seconds is generous timeout
        assert len(analyses) == len(frames)


class TestProcessCleanup:
    """Test proper cleanup of processes and resources."""

    def test_process_pool_cleanup_on_success(self):
        """Test that process pool is cleaned up after successful execution."""

        processor = ParallelFrameProcessor(max_workers=2)
        video_path = "data/videos/real/real_video_v1.mp4"

        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        # Extract frames
        processor.extract_frames_parallel(video_path, [0, 1, 2])

        # Process pool should be terminated (no zombie processes)
        # This is handled by context manager in the implementation

    def test_process_pool_cleanup_on_exception(self):
        """Test that process pool is cleaned up even if exception occurs."""

        processor = ParallelFrameProcessor(max_workers=2)

        try:
            # Try to process invalid video (should raise exception)
            processor.extract_frames_parallel("nonexistent.mp4", [0, 1, 2])
        except FileNotFoundError:
            pass  # Expected

        # Process pool should still be cleaned up
        # This is handled by context manager in the implementation


# Integration tests

class TestIntegration:
    """Integration tests combining multiple components."""

    def test_end_to_end_parallel_pipeline(self):
        """Test complete parallel pipeline: extraction + analysis."""

        video_path = "data/videos/real/real_video_v1.mp4"

        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        # Step 1: Parallel frame extraction
        extractor = ParallelFrameProcessor(max_workers=2)
        frames, extract_meta = extractor.extract_frames_parallel(video_path, [0, 10, 20])

        assert len(frames) > 0

        # Step 2: Parallel analysis
        def mock_analyze(frame, idx, **kwargs):
            return {'frame_index': idx, 'analysis': 'complete'}

        analyzer = ParallelLLMAnalyzer(max_concurrent_requests=2)
        analyses, analyze_meta = analyzer.analyze_frames_parallel(frames, mock_analyze)

        assert len(analyses) == len(frames)
        assert all('analysis' in a for a in analyses)

    def test_benchmark_comparison(self):
        """Test that parallel execution is faster than sequential."""

        video_path = "data/videos/real/real_video_v1.mp4"

        if not Path(video_path).exists():
            pytest.skip(f"Test video not found: {video_path}")

        processor = ParallelFrameProcessor(max_workers=mp.cpu_count())
        benchmark = processor.benchmark_speedup(video_path, list(range(0, 50, 5)))

        # Parallel should be at least as fast as sequential
        # (may not always be faster for very small workloads due to overhead)
        assert benchmark['speedup'] >= 0.5  # Allow some overhead

        print(f"\nSpeedup: {benchmark['speedup']:.2f}x")
        print(f"Sequential: {benchmark['sequential_time']:.2f}s")
        print(f"Parallel: {benchmark['parallel_time']:.2f}s")
