"""
Video Processing Module

Handles video loading, frame extraction, and metadata extraction
for deepfake detection analysis.
"""

import cv2
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np


class VideoProcessor:
    """
    Processes MP4 videos for deepfake detection analysis.

    Handles:
    - Video validation and metadata extraction
    - Frame sampling and extraction
    - Preprocessing and normalization
    """

    def __init__(self, video_path: str, num_frames: int = 10):
        """
        Initialize video processor.

        Args:
            video_path: Path to MP4 video file
            num_frames: Number of frames to extract (default: 10)
        """
        self.video_path = Path(video_path)
        self.num_frames = num_frames
        self.metadata = None
        self.frames = []

        # Validate video exists
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not self.video_path.suffix.lower() == '.mp4':
            raise ValueError(f"Only MP4 files supported, got: {self.video_path.suffix}")

    def extract_metadata(self) -> Dict:
        """
        Extract video metadata using ffprobe.

        Returns:
            Dictionary containing video metadata (resolution, duration, fps, codec, etc.)
        """
        try:
            # Use ffprobe to extract metadata
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(self.video_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            probe_data = json.loads(result.stdout)

            # Extract video stream info
            video_stream = None
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break

            if not video_stream:
                raise ValueError("No video stream found in file")

            # Parse metadata
            format_info = probe_data.get('format', {})

            self.metadata = {
                'filename': self.video_path.name,
                'path': str(self.video_path),
                'duration': float(format_info.get('duration', 0)),
                'size_bytes': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                'codec': video_stream.get('codec_name', 'unknown'),
                'fps': self._parse_fps(video_stream.get('r_frame_rate', '0/1')),
                'total_frames': int(video_stream.get('nb_frames', 0)),
            }

            return self.metadata

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract metadata with ffprobe: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse ffprobe output: {e}")

    def _parse_fps(self, fps_string: str) -> float:
        """
        Parse FPS from fraction string (e.g., '30000/1001').

        Args:
            fps_string: FPS as fraction string

        Returns:
            FPS as float
        """
        try:
            numerator, denominator = fps_string.split('/')
            return float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def extract_frames(self, sampling_strategy: str = 'uniform') -> List[np.ndarray]:
        """
        Extract frames from video using specified sampling strategy.

        Args:
            sampling_strategy: Frame sampling strategy ('uniform', 'keyframes', or 'adaptive')

        Returns:
            List of frame images as numpy arrays (RGB format)
        """
        cap = cv2.VideoCapture(str(self.video_path))

        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {self.video_path}")

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames == 0:
                raise ValueError("Video has no frames")

            # Determine frame indices to extract
            if sampling_strategy == 'uniform':
                frame_indices = self._uniform_sampling(total_frames)
            elif sampling_strategy == 'keyframes':
                frame_indices = self._keyframe_sampling(cap, total_frames)
            elif sampling_strategy == 'adaptive':
                frame_indices = self._adaptive_sampling(cap, total_frames)
            else:
                raise ValueError(f"Unknown sampling strategy: {sampling_strategy}")

            # Extract frames
            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()

                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)

            self.frames = frames
            return frames

        finally:
            cap.release()

    def _uniform_sampling(self, total_frames: int) -> List[int]:
        """
        Uniform frame sampling - evenly spaced frames.

        Args:
            total_frames: Total number of frames in video

        Returns:
            List of frame indices to extract
        """
        if total_frames <= self.num_frames:
            # If video has fewer frames than requested, take all
            return list(range(total_frames))

        # Calculate evenly spaced indices
        step = total_frames / self.num_frames
        indices = [int(i * step) for i in range(self.num_frames)]

        return indices

    def _keyframe_sampling(self, cap, total_frames: int) -> List[int]:
        """
        Keyframe-based sampling (simplified - falls back to uniform).

        Note: Proper keyframe detection requires codec-level analysis.
        This is a simplified version using uniform sampling.

        Args:
            cap: OpenCV video capture object
            total_frames: Total number of frames

        Returns:
            List of frame indices
        """
        # For simplicity, fall back to uniform sampling
        # Full keyframe detection would require codec-level access
        return self._uniform_sampling(total_frames)

    def _adaptive_sampling(self, cap, total_frames: int) -> List[int]:
        """
        Adaptive sampling based on scene changes (simplified).

        Args:
            cap: OpenCV video capture object
            total_frames: Total number of frames

        Returns:
            List of frame indices
        """
        # Simplified adaptive sampling - includes more frames from beginning/end
        # where artifacts are often more visible

        indices = []

        # Take more samples from first and last 20% of video
        first_20_percent = int(total_frames * 0.2)
        last_20_percent = int(total_frames * 0.8)

        # First 20%: 40% of frames
        num_first = int(self.num_frames * 0.4)
        step = max(1, first_20_percent // num_first)
        indices.extend(range(0, first_20_percent, step)[:num_first])

        # Middle 60%: 20% of frames
        num_middle = int(self.num_frames * 0.2)
        step = max(1, (last_20_percent - first_20_percent) // num_middle)
        indices.extend(range(first_20_percent, last_20_percent, step)[:num_middle])

        # Last 20%: 40% of frames
        num_last = self.num_frames - len(indices)
        step = max(1, (total_frames - last_20_percent) // num_last)
        indices.extend(range(last_20_percent, total_frames, step)[:num_last])

        return sorted(list(set(indices)))[:self.num_frames]

    def get_frame_timestamps(self) -> List[float]:
        """
        Get timestamps (in seconds) for extracted frames.

        Returns:
            List of timestamps corresponding to extracted frames
        """
        if not self.metadata:
            self.extract_metadata()

        if not self.frames:
            raise ValueError("No frames extracted yet. Call extract_frames() first.")

        fps = self.metadata.get('fps', 30.0)
        total_frames = self.metadata.get('total_frames', len(self.frames))

        # Calculate timestamps based on uniform distribution
        step = total_frames / len(self.frames)
        timestamps = [i * step / fps for i in range(len(self.frames))]

        return timestamps

    def save_frames(self, output_dir: str, prefix: str = "frame") -> List[Path]:
        """
        Save extracted frames to disk.

        Args:
            output_dir: Directory to save frames
            prefix: Filename prefix for saved frames

        Returns:
            List of paths to saved frame files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_paths = []
        for i, frame in enumerate(self.frames):
            # Convert RGB back to BGR for saving with OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            filename = output_path / f"{prefix}_{i:03d}.jpg"
            cv2.imwrite(str(filename), frame_bgr)
            saved_paths.append(filename)

        return saved_paths

    def process(self, sampling_strategy: str = 'uniform') -> Dict:
        """
        Complete processing pipeline: extract metadata and frames.

        Args:
            sampling_strategy: Frame sampling strategy

        Returns:
            Dictionary with metadata and frame information
        """
        # Extract metadata
        metadata = self.extract_metadata()

        # Extract frames
        frames = self.extract_frames(sampling_strategy)

        # Get timestamps
        timestamps = self.get_frame_timestamps()

        return {
            'metadata': metadata,
            'frames': frames,
            'num_frames': len(frames),
            'timestamps': timestamps,
            'sampling_strategy': sampling_strategy
        }


def validate_video_file(video_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a video file exists and is a valid MP4.

    Args:
        video_path: Path to video file

    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(video_path)

    if not path.exists():
        return False, f"File not found: {video_path}"

    if not path.is_file():
        return False, f"Not a file: {video_path}"

    if path.suffix.lower() != '.mp4':
        return False, f"Not an MP4 file: {video_path}"

    # Try to open with OpenCV
    try:
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return False, f"Cannot open video file: {video_path}"

        # Check if video has frames
        ret, _ = cap.read()
        cap.release()

        if not ret:
            return False, f"Video has no readable frames: {video_path}"

        return True, None

    except Exception as e:
        return False, f"Error validating video: {str(e)}"
