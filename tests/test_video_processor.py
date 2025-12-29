"""
Unit tests for video_processor module.

Tests frame extraction, metadata parsing, and sampling strategies.
FFmpeg calls are mocked to avoid external dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pathlib import Path
import json

from src.video_processor import VideoProcessor, validate_video_file


class TestFrameSampling:
    """Test frame sampling strategies."""

    def test_uniform_sampling_basic(self):
        """Test uniform sampling returns correct number of indices."""
        processor = VideoProcessor.__new__(VideoProcessor)
        processor.num_frames = 5

        indices = processor._uniform_sampling(total_frames=100)

        assert len(indices) == 5
        assert indices == [0, 20, 40, 60, 80]  # Evenly spaced

    def test_uniform_sampling_fewer_frames_than_requested(self):
        """Test uniform sampling when video has fewer frames than requested."""
        processor = VideoProcessor.__new__(VideoProcessor)
        processor.num_frames = 10

        indices = processor._uniform_sampling(total_frames=5)

        assert len(indices) == 5  # Returns all available frames
        assert indices == [0, 1, 2, 3, 4]

    def test_uniform_sampling_exact_match(self):
        """Test uniform sampling when frames match request exactly."""
        processor = VideoProcessor.__new__(VideoProcessor)
        processor.num_frames = 10

        indices = processor._uniform_sampling(total_frames=10)

        assert len(indices) == 10

    def test_adaptive_sampling_distribution(self):
        """Test adaptive sampling emphasizes beginning and end."""
        processor = VideoProcessor.__new__(VideoProcessor)
        processor.num_frames = 10

        indices = processor._adaptive_sampling(None, total_frames=100)

        assert len(indices) == 10
        # Should have more samples from first 20% and last 20%
        first_20_percent = sum(1 for i in indices if i < 20)
        last_20_percent = sum(1 for i in indices if i >= 80)
        middle_60_percent = sum(1 for i in indices if 20 <= i < 80)

        # Adaptive should have more at edges than middle
        assert first_20_percent + last_20_percent > middle_60_percent


class TestVideoValidation:
    """Test video file validation."""

    def test_validate_video_file_not_exists(self):
        """Test validation fails for non-existent file."""
        is_valid, error = validate_video_file("/nonexistent/path/video.mp4")

        assert is_valid is False
        assert "not found" in error.lower()

    def test_validate_video_file_wrong_extension(self, tmp_path):
        """Test validation fails for non-MP4 file."""
        # Create a text file
        test_file = tmp_path / "test.txt"
        test_file.write_text("not a video")

        is_valid, error = validate_video_file(str(test_file))

        assert is_valid is False
        assert "mp4" in error.lower()


class TestMetadataExtraction:
    """Test metadata extraction with mocked FFmpeg."""

    @patch('subprocess.run')
    def test_extract_metadata_success(self, mock_run):
        """Test successful metadata extraction."""
        # Mock FFmpeg response
        mock_ffprobe_output = {
            "streams": [{
                "codec_type": "video",
                "codec_name": "h264",
                "width": 1920,
                "height": 1080,
                "r_frame_rate": "30/1",
                "nb_frames": "150"
            }],
            "format": {
                "duration": "5.0",
                "size": "1000000",
                "bit_rate": "200000"
            }
        }

        mock_run.return_value = Mock(
            stdout=json.dumps(mock_ffprobe_output),
            returncode=0
        )

        # Create processor with mocked path
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.suffix', '.mp4'):
                processor = VideoProcessor.__new__(VideoProcessor)
                processor.video_path = Path("/fake/video.mp4")
                processor.num_frames = 10

                metadata = processor.extract_metadata()

        assert metadata['width'] == 1920
        assert metadata['height'] == 1080
        assert metadata['resolution'] == "1920x1080"
        assert metadata['codec'] == "h264"
        assert metadata['duration'] == 5.0
        assert metadata['fps'] == 30.0

    def test_parse_fps_standard(self):
        """Test FPS parsing from fraction string."""
        processor = VideoProcessor.__new__(VideoProcessor)

        fps = processor._parse_fps("30/1")
        assert fps == 30.0

        fps = processor._parse_fps("30000/1001")
        assert abs(fps - 29.97) < 0.01

    def test_parse_fps_invalid(self):
        """Test FPS parsing with invalid input."""
        processor = VideoProcessor.__new__(VideoProcessor)

        fps = processor._parse_fps("invalid")
        assert fps == 0.0

        fps = processor._parse_fps("30/0")  # Division by zero
        assert fps == 0.0


class TestFrameExtraction:
    """Test frame extraction with mocked OpenCV."""

    @patch('cv2.VideoCapture')
    def test_extract_frames_count(self, mock_videocapture):
        """Test correct number of frames extracted."""
        # Mock OpenCV VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30  # 30 frames total

        # Mock frame reading
        fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, fake_frame)

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)
            frames = processor.extract_frames(sampling_strategy='uniform')

        assert len(frames) == 5
        assert all(isinstance(f, np.ndarray) for f in frames)

    @patch('cv2.VideoCapture')
    def test_extract_frames_empty_video(self, mock_videocapture):
        """Test extraction fails gracefully on empty video."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 0  # Zero frames

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=10)

            with pytest.raises(ValueError, match="no frames"):
                processor.extract_frames()


class TestTimestamps:
    """Test timestamp calculation."""

    def test_get_frame_timestamps(self):
        """Test timestamp calculation for extracted frames."""
        processor = VideoProcessor.__new__(VideoProcessor)
        processor.num_frames = 10
        processor.metadata = {
            'fps': 30.0,
            'total_frames': 150
        }
        processor.frames = [None] * 5  # 5 frames extracted

        timestamps = processor.get_frame_timestamps()

        assert len(timestamps) == 5
        assert timestamps[0] == 0.0  # First frame at 0
        assert timestamps[-1] > timestamps[0]  # Last frame later
        assert all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))  # Sorted
