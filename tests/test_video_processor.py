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
import subprocess

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

    @patch('subprocess.run')
    def test_get_frame_timestamps_extracts_metadata_if_missing(self, mock_run):
        """Test that get_frame_timestamps extracts metadata if not present."""
        mock_ffprobe_output = {
            "streams": [{
                "codec_type": "video",
                "r_frame_rate": "30/1",
                "width": 1920,
                "height": 1080,
                "nb_frames": "150"
            }],
            "format": {"duration": "5.0"}
        }

        mock_run.return_value = Mock(
            stdout=json.dumps(mock_ffprobe_output),
            returncode=0
        )

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)
            processor.frames = [None] * 5

            # metadata is None initially, should call extract_metadata
            timestamps = processor.get_frame_timestamps()

            assert processor.metadata is not None
            assert len(timestamps) == 5

    def test_get_frame_timestamps_no_frames_error(self):
        """Test that get_frame_timestamps raises error if no frames extracted."""
        processor = VideoProcessor.__new__(VideoProcessor)
        processor.metadata = {'fps': 30.0, 'total_frames': 150}
        processor.frames = []  # No frames

        with pytest.raises(ValueError, match="No frames extracted"):
            processor.get_frame_timestamps()


class TestInitializationErrors:
    """Test initialization error handling."""

    def test_init_file_not_found(self):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            VideoProcessor("/nonexistent/path/video.mp4")

    def test_init_wrong_extension(self, tmp_path):
        """Test initialization with non-MP4 file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("not a video")

        with pytest.raises(ValueError, match="Only MP4 files supported"):
            VideoProcessor(str(test_file))


class TestMetadataExtractionErrors:
    """Test metadata extraction error handling."""

    @patch('subprocess.run')
    def test_extract_metadata_no_video_stream(self, mock_run):
        """Test metadata extraction when no video stream found."""
        # Mock FFmpeg response with no video stream
        mock_ffprobe_output = {
            "streams": [{
                "codec_type": "audio"  # Only audio, no video
            }],
            "format": {"duration": "5.0"}
        }

        mock_run.return_value = Mock(
            stdout=json.dumps(mock_ffprobe_output),
            returncode=0
        )

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor.__new__(VideoProcessor)
            processor.video_path = Path("/fake/video.mp4")
            processor.num_frames = 10

            with pytest.raises(ValueError, match="No video stream found"):
                processor.extract_metadata()

    @patch('subprocess.run')
    def test_extract_metadata_subprocess_error(self, mock_run):
        """Test metadata extraction when ffprobe fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffprobe')

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor.__new__(VideoProcessor)
            processor.video_path = Path("/fake/video.mp4")
            processor.num_frames = 10

            with pytest.raises(RuntimeError, match="Failed to extract metadata"):
                processor.extract_metadata()

    @patch('subprocess.run')
    def test_extract_metadata_json_error(self, mock_run):
        """Test metadata extraction when JSON parsing fails."""
        mock_run.return_value = Mock(
            stdout="invalid json{{{",
            returncode=0
        )

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor.__new__(VideoProcessor)
            processor.video_path = Path("/fake/video.mp4")
            processor.num_frames = 10

            with pytest.raises(RuntimeError, match="Failed to parse"):
                processor.extract_metadata()


class TestFrameExtractionErrors:
    """Test frame extraction error handling."""

    @patch('cv2.VideoCapture')
    def test_extract_frames_failed_to_open(self, mock_videocapture):
        """Test extraction when video cannot be opened."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)

            with pytest.raises(RuntimeError, match="Failed to open video"):
                processor.extract_frames()

    @patch('cv2.VideoCapture')
    def test_extract_frames_invalid_strategy(self, mock_videocapture):
        """Test extraction with invalid sampling strategy."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)

            with pytest.raises(ValueError, match="Unknown sampling strategy"):
                processor.extract_frames(sampling_strategy='invalid_strategy')

    @patch('cv2.VideoCapture')
    def test_extract_frames_keyframe_strategy(self, mock_videocapture):
        """Test extraction with keyframe sampling strategy."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, fake_frame)

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)
            frames = processor.extract_frames(sampling_strategy='keyframes')

            assert len(frames) == 5

    @patch('cv2.VideoCapture')
    def test_extract_frames_adaptive_strategy(self, mock_videocapture):
        """Test extraction with adaptive sampling strategy."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, fake_frame)

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=10)
            frames = processor.extract_frames(sampling_strategy='adaptive')

            assert len(frames) == 10


class TestSaveFrames:
    """Test frame saving functionality."""

    @patch('cv2.imwrite')
    def test_save_frames(self, mock_imwrite, tmp_path):
        """Test saving extracted frames to disk."""
        mock_imwrite.return_value = True

        processor = VideoProcessor.__new__(VideoProcessor)
        processor.frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(3)
        ]

        output_dir = tmp_path / "output"
        saved_paths = processor.save_frames(str(output_dir), prefix="test")

        assert len(saved_paths) == 3
        assert all(p.name.startswith("test_") for p in saved_paths)
        assert mock_imwrite.call_count == 3


class TestCompleteProcessing:
    """Test complete processing pipeline."""

    @patch('cv2.VideoCapture')
    @patch('subprocess.run')
    def test_process_complete_pipeline(self, mock_run, mock_videocapture):
        """Test complete processing pipeline."""
        # Mock ffprobe
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

        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 150

        fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, fake_frame)

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)
            result = processor.process(sampling_strategy='uniform')

            assert 'metadata' in result
            assert 'frames' in result
            assert 'num_frames' in result
            assert 'timestamps' in result
            assert 'sampling_strategy' in result
            assert result['num_frames'] == 5
            assert result['sampling_strategy'] == 'uniform'


class TestGetMetadata:
    """Test get_metadata method."""

    @patch('subprocess.run')
    def test_get_metadata_cached(self, mock_run):
        """Test get_metadata returns cached metadata."""
        mock_ffprobe_output = {
            "streams": [{
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
                "r_frame_rate": "30/1",
                "nb_frames": "150"
            }],
            "format": {"duration": "5.0"}
        }

        mock_run.return_value = Mock(
            stdout=json.dumps(mock_ffprobe_output),
            returncode=0
        )

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)

            # First call extracts metadata
            metadata1 = processor.get_metadata()

            # Second call should use cached version
            metadata2 = processor.get_metadata()

            assert metadata1 == metadata2
            assert mock_run.call_count == 1  # Only called once


class TestGetFrameIndices:
    """Test get_frame_indices method."""

    @patch('cv2.VideoCapture')
    def test_get_frame_indices_uniform(self, mock_videocapture):
        """Test getting frame indices with uniform strategy."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=10)
            indices = processor.get_frame_indices(sampling_strategy='uniform')

            assert len(indices) == 10
            assert indices == [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

    @patch('cv2.VideoCapture')
    def test_get_frame_indices_custom_num_frames(self, mock_videocapture):
        """Test getting frame indices with custom num_frames."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=10)

            # Get indices for 5 frames instead of 10
            indices = processor.get_frame_indices(sampling_strategy='uniform', num_frames=5)

            assert len(indices) == 5
            # Check that original num_frames is preserved
            assert processor.num_frames == 10

    @patch('cv2.VideoCapture')
    def test_get_frame_indices_keyframes(self, mock_videocapture):
        """Test getting frame indices with keyframes strategy."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=10)
            indices = processor.get_frame_indices(sampling_strategy='keyframes')

            assert len(indices) == 10

    @patch('cv2.VideoCapture')
    def test_get_frame_indices_adaptive(self, mock_videocapture):
        """Test getting frame indices with adaptive strategy."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=10)
            indices = processor.get_frame_indices(sampling_strategy='adaptive')

            assert len(indices) == 10

    @patch('cv2.VideoCapture')
    def test_get_frame_indices_failed_to_open(self, mock_videocapture):
        """Test get_frame_indices when video cannot be opened."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)

            with pytest.raises(RuntimeError, match="Failed to open video"):
                processor.get_frame_indices()

    @patch('cv2.VideoCapture')
    def test_get_frame_indices_no_frames(self, mock_videocapture):
        """Test get_frame_indices when video has no frames."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 0

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)

            with pytest.raises(ValueError, match="no frames"):
                processor.get_frame_indices()

    @patch('cv2.VideoCapture')
    def test_get_frame_indices_invalid_strategy(self, mock_videocapture):
        """Test get_frame_indices with invalid strategy."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100

        mock_videocapture.return_value = mock_cap

        with patch('pathlib.Path.exists', return_value=True):
            processor = VideoProcessor("/fake/video.mp4", num_frames=5)

            with pytest.raises(ValueError, match="Unknown sampling strategy"):
                processor.get_frame_indices(sampling_strategy='invalid')


class TestValidateVideoFileAdvanced:
    """Test advanced video file validation."""

    def test_validate_video_file_not_a_file(self, tmp_path):
        """Test validation when path is a directory."""
        directory = tmp_path / "not_a_file"
        directory.mkdir()

        is_valid, error = validate_video_file(str(directory))

        assert is_valid is False
        assert "Not a file" in error

    @patch('cv2.VideoCapture')
    def test_validate_video_file_cannot_open(self, mock_videocapture, tmp_path):
        """Test validation when video cannot be opened."""
        test_file = tmp_path / "test.mp4"
        test_file.write_text("fake video content")

        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_videocapture.return_value = mock_cap

        is_valid, error = validate_video_file(str(test_file))

        assert is_valid is False
        assert "Cannot open" in error

    @patch('cv2.VideoCapture')
    def test_validate_video_file_no_readable_frames(self, mock_videocapture, tmp_path):
        """Test validation when video has no readable frames."""
        test_file = tmp_path / "test.mp4"
        test_file.write_text("fake video content")

        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_videocapture.return_value = mock_cap

        is_valid, error = validate_video_file(str(test_file))

        assert is_valid is False
        assert "no readable frames" in error

    @patch('cv2.VideoCapture')
    def test_validate_video_file_exception(self, mock_videocapture, tmp_path):
        """Test validation when exception occurs."""
        test_file = tmp_path / "test.mp4"
        test_file.write_text("fake video content")

        mock_videocapture.side_effect = Exception("Unexpected error")

        is_valid, error = validate_video_file(str(test_file))

        assert is_valid is False
        assert "Error validating video" in error

    @patch('cv2.VideoCapture')
    def test_validate_video_file_success(self, mock_videocapture, tmp_path):
        """Test successful video validation."""
        test_file = tmp_path / "test.mp4"
        test_file.write_text("fake video content")

        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_videocapture.return_value = mock_cap

        is_valid, error = validate_video_file(str(test_file))

        assert is_valid is True
        assert error is None
