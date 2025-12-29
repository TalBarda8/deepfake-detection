"""
Unit tests for detector module.

Tests detection pipeline orchestration with mocked components.
Tests classification logic and result aggregation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from datetime import datetime

from src.detector import DeepfakeDetector, create_detector


class TestDetectorInitialization:
    """Test detector initialization."""

    def test_init_default_parameters(self):
        """Test detector initialization with defaults."""
        detector = DeepfakeDetector(api_provider='mock')

        assert detector.api_provider == 'mock'
        assert detector.num_frames == 10
        assert detector.sampling_strategy == 'uniform'
        assert detector.llm_analyzer is not None

    def test_init_custom_parameters(self):
        """Test detector initialization with custom parameters."""
        detector = DeepfakeDetector(
            api_provider='mock',
            num_frames=15,
            sampling_strategy='adaptive'
        )

        assert detector.num_frames == 15
        assert detector.sampling_strategy == 'adaptive'

    def test_factory_function(self):
        """Test detector factory function."""
        detector = create_detector(api_provider='mock', num_frames=5)

        assert isinstance(detector, DeepfakeDetector)
        assert detector.num_frames == 5


class TestFrameSelection:
    """Test key frame selection logic."""

    def test_select_key_frames_basic(self):
        """Test key frame selection with standard input."""
        detector = DeepfakeDetector(api_provider='mock')

        indices = detector._select_key_frames(total_frames=10, max_frames=5)

        assert len(indices) == 5
        assert 0 in indices  # Should include first frame
        assert 9 in indices  # Should include last frame
        assert all(0 <= i < 10 for i in indices)  # All within range

    def test_select_key_frames_fewer_than_max(self):
        """Test key frame selection when total < max."""
        detector = DeepfakeDetector(api_provider='mock')

        indices = detector._select_key_frames(total_frames=3, max_frames=5)

        assert len(indices) == 3
        assert indices == [0, 1, 2]

    def test_select_key_frames_sorted(self):
        """Test that selected frames are in order."""
        detector = DeepfakeDetector(api_provider='mock')

        indices = detector._select_key_frames(total_frames=20, max_frames=5)

        assert indices == sorted(indices)

    def test_select_key_frames_no_duplicates(self):
        """Test that no frame indices are duplicated."""
        detector = DeepfakeDetector(api_provider='mock')

        indices = detector._select_key_frames(total_frames=20, max_frames=5)

        assert len(indices) == len(set(indices))


class TestDetectionPipeline:
    """Test complete detection pipeline with mocks."""

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    def test_detect_success(self, mock_processor_class, mock_validate):
        """Test successful detection pipeline."""
        # Mock validation
        mock_validate.return_value = (True, None)

        # Mock video processor
        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {
                'filename': 'test.mp4',
                'duration': 5.0,
                'resolution': '1920x1080'
            },
            'frames': [np.zeros((480, 640, 3)) for _ in range(10)],
            'num_frames': 10,
            'timestamps': [0.0, 0.5, 1.0, 1.5, 2.0],
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        # Create detector and run
        detector = DeepfakeDetector(api_provider='mock', num_frames=10)
        results = detector.detect('/fake/video.mp4')

        # Verify results structure
        assert 'classification' in results
        assert 'confidence' in results
        assert 'reasoning' in results
        assert 'metadata' in results
        assert 'num_frames_analyzed' in results
        assert results['sampling_strategy'] == 'uniform'

    @patch('src.detector.validate_video_file')
    def test_detect_invalid_video(self, mock_validate):
        """Test detection fails gracefully on invalid video."""
        mock_validate.return_value = (False, "File not found")

        detector = DeepfakeDetector(api_provider='mock')

        with pytest.raises(ValueError, match="Invalid video"):
            detector.detect('/nonexistent/video.mp4')

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    def test_detect_handles_exceptions(self, mock_processor_class, mock_validate):
        """Test detection handles exceptions in pipeline."""
        mock_validate.return_value = (True, None)

        # Make processor raise exception
        mock_processor_class.side_effect = RuntimeError("Processing failed")

        detector = DeepfakeDetector(api_provider='mock')

        with pytest.raises(RuntimeError, match="Detection failed"):
            detector.detect('/fake/video.mp4')


class TestVerdictSynthesis:
    """Test verdict synthesis from analyses."""

    def test_synthesize_verdict_aggregates_evidence(self):
        """Test that verdict synthesis aggregates all evidence."""
        detector = DeepfakeDetector(api_provider='mock')

        frame_analyses = [
            {'frame_index': 0, 'analysis': 'Smoothing detected'},
            {'frame_index': 5, 'analysis': 'Lighting inconsistent'}
        ]

        temporal_analysis = {
            'num_frames': 10,
            'analysis': 'Temporal artifacts present'
        }

        metadata = {
            'filename': 'test.mp4',
            'duration': 5.0,
            'resolution': '1920x1080'
        }

        verdict = detector._synthesize_verdict(
            frame_analyses, temporal_analysis, metadata
        )

        assert 'classification' in verdict
        assert 'confidence' in verdict
        assert 'reasoning' in verdict


class TestBatchProcessing:
    """Test batch detection functionality."""

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    def test_batch_detect_multiple_videos(self, mock_processor_class, mock_validate):
        """Test batch processing of multiple videos."""
        mock_validate.return_value = (True, None)

        # Mock processor
        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {'filename': 'test.mp4', 'duration': 5.0},
            'frames': [np.zeros((100, 100, 3)) for _ in range(5)],
            'num_frames': 5,
            'timestamps': [0, 1, 2, 3, 4],
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        detector = DeepfakeDetector(api_provider='mock')

        video_paths = ['/fake/video1.mp4', '/fake/video2.mp4']
        results = detector.batch_detect(video_paths)

        assert len(results) == 2
        assert '/fake/video1.mp4' in results
        assert '/fake/video2.mp4' in results

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    def test_batch_detect_handles_individual_failures(self, mock_processor_class, mock_validate):
        """Test batch processing continues on individual failures."""
        # First video valid, second invalid
        mock_validate.side_effect = [
            (True, None),
            (False, "Invalid video"),
            (True, None)
        ]

        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {'filename': 'test.mp4', 'duration': 5.0},
            'frames': [np.zeros((100, 100, 3)) for _ in range(5)],
            'num_frames': 5,
            'timestamps': [0, 1, 2, 3, 4],
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        detector = DeepfakeDetector(api_provider='mock')

        video_paths = ['/video1.mp4', '/invalid.mp4', '/video3.mp4']
        results = detector.batch_detect(video_paths)

        # Should have results for all 3, but middle one has error
        assert len(results) == 3
        assert 'error' in results['/invalid.mp4']
        assert 'classification' in results['/video1.mp4']


class TestDetectAndReport:
    """Test detection with reporting functionality."""

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    @patch('src.detector.OutputFormatter')
    def test_detect_and_report_console_output(self, mock_formatter, mock_processor_class, mock_validate):
        """Test detect_and_report prints to console."""
        mock_validate.return_value = (True, None)

        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {'filename': 'test.mp4', 'duration': 5.0},
            'frames': [np.zeros((100, 100, 3)) for _ in range(5)],
            'num_frames': 5,
            'timestamps': [0, 1, 2, 3, 4],
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        detector = DeepfakeDetector(api_provider='mock')
        results = detector.detect_and_report('/fake/video.mp4')

        # Verify formatter was called
        mock_formatter.print_console_report.assert_called_once()
        assert 'classification' in results

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    @patch('src.detector.OutputFormatter')
    def test_detect_and_report_saves_files(self, mock_formatter, mock_processor_class, mock_validate):
        """Test detect_and_report saves output files when requested."""
        mock_validate.return_value = (True, None)

        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {'filename': 'test.mp4', 'duration': 5.0},
            'frames': [np.zeros((100, 100, 3)) for _ in range(5)],
            'num_frames': 5,
            'timestamps': [0, 1, 2, 3, 4],
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        detector = DeepfakeDetector(api_provider='mock')
        results = detector.detect_and_report(
            '/fake/video.mp4',
            output_json='/tmp/result.json',
            output_txt='/tmp/report.txt'
        )

        # Verify save methods were called
        mock_formatter.save_json.assert_called_once()
        mock_formatter.save_text_report.assert_called_once()


class TestResultStructure:
    """Test structure of detection results."""

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    def test_result_has_required_fields(self, mock_processor_class, mock_validate):
        """Test detection result contains all required fields."""
        mock_validate.return_value = (True, None)

        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {
                'filename': 'test.mp4',
                'duration': 5.0,
                'resolution': '1920x1080',
                'fps': 30.0
            },
            'frames': [np.zeros((100, 100, 3)) for _ in range(10)],
            'num_frames': 10,
            'timestamps': list(range(10)),
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        detector = DeepfakeDetector(api_provider='mock', num_frames=10)
        results = detector.detect('/fake/video.mp4')

        # Required fields
        required_fields = [
            'classification',
            'confidence',
            'reasoning',
            'metadata',
            'num_frames_analyzed',
            'sampling_strategy',
            'model_name',
            'api_provider',
            'timestamp'
        ]

        for field in required_fields:
            assert field in results, f"Missing required field: {field}"

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    def test_result_classification_valid(self, mock_processor_class, mock_validate):
        """Test classification is one of valid values."""
        mock_validate.return_value = (True, None)

        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {'filename': 'test.mp4', 'duration': 5.0},
            'frames': [np.zeros((100, 100, 3)) for _ in range(5)],
            'num_frames': 5,
            'timestamps': [0, 1, 2, 3, 4],
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        detector = DeepfakeDetector(api_provider='mock')
        results = detector.detect('/fake/video.mp4')

        valid_classifications = [
            'REAL', 'LIKELY REAL', 'UNCERTAIN', 'LIKELY FAKE', 'FAKE'
        ]
        assert results['classification'] in valid_classifications

    @patch('src.detector.validate_video_file')
    @patch('src.detector.VideoProcessor')
    def test_result_confidence_range(self, mock_processor_class, mock_validate):
        """Test confidence is in valid range 0-100."""
        mock_validate.return_value = (True, None)

        mock_processor = MagicMock()
        mock_processor.process.return_value = {
            'metadata': {'filename': 'test.mp4', 'duration': 5.0},
            'frames': [np.zeros((100, 100, 3)) for _ in range(5)],
            'num_frames': 5,
            'timestamps': [0, 1, 2, 3, 4],
            'sampling_strategy': 'uniform'
        }
        mock_processor_class.return_value = mock_processor

        detector = DeepfakeDetector(api_provider='mock')
        results = detector.detect('/fake/video.mp4')

        assert 0 <= results['confidence'] <= 100
