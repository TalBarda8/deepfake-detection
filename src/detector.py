"""
Deepfake Detector Module

Main orchestration logic for the deepfake detection system.
Coordinates video processing, LLM analysis, and result generation.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .video_processor import VideoProcessor, validate_video_file
from .llm_analyzer import LLMAnalyzer
from .output_formatter import OutputFormatter


class DeepfakeDetector:
    """
    Main deepfake detection orchestrator.

    Coordinates the complete detection pipeline:
    1. Video processing and frame extraction
    2. LLM-based frame analysis
    3. Temporal consistency analysis
    4. Synthesis and verdict generation
    """

    def __init__(
        self,
        api_provider: str = "anthropic",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        num_frames: int = 10,
        sampling_strategy: str = "uniform",
        prompts_dir: str = "prompts",
        verbose: bool = False
    ):
        """
        Initialize deepfake detector.

        Args:
            api_provider: LLM provider ('anthropic', 'openai', or 'mock')
            model_name: Specific model to use (optional)
            api_key: API key (optional, reads from environment)
            num_frames: Number of frames to extract from video
            sampling_strategy: Frame sampling strategy ('uniform', 'keyframes', 'adaptive')
            prompts_dir: Directory containing prompt templates
            verbose: Enable verbose logging
        """
        self.api_provider = api_provider
        self.model_name = model_name
        self.num_frames = num_frames
        self.sampling_strategy = sampling_strategy
        self.verbose = verbose

        # Initialize LLM analyzer
        self.llm_analyzer = LLMAnalyzer(
            api_provider=api_provider,
            model_name=model_name,
            api_key=api_key,
            prompts_dir=prompts_dir
        )

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        level = logging.DEBUG if self.verbose else logging.INFO

        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger('DeepfakeDetector')

    def detect(self, video_path: str) -> Dict[str, Any]:
        """
        Perform complete deepfake detection on a video.

        Args:
            video_path: Path to MP4 video file

        Returns:
            Detection results dictionary

        Raises:
            FileNotFoundError: If video file not found
            ValueError: If video file invalid
            RuntimeError: If detection fails
        """
        self.logger.info(f"Starting deepfake detection on: {video_path}")

        # Validate video
        is_valid, error_msg = validate_video_file(video_path)
        if not is_valid:
            raise ValueError(f"Invalid video file: {error_msg}")

        try:
            # Step 1: Process video (extract metadata and frames)
            self.logger.info("Step 1/4: Processing video and extracting frames...")
            video_data = self._process_video(video_path)

            # Step 2: Analyze individual frames
            self.logger.info("Step 2/4: Analyzing individual frames...")
            frame_analyses = self._analyze_frames(
                video_data['frames'],
                video_data['metadata']
            )

            # Step 3: Analyze temporal consistency
            self.logger.info("Step 3/4: Analyzing temporal consistency...")
            temporal_analysis = self._analyze_temporal(
                video_data['frames'],
                list(range(len(video_data['frames'])))
            )

            # Step 4: Synthesize final verdict
            self.logger.info("Step 4/4: Synthesizing final verdict...")
            verdict = self._synthesize_verdict(
                frame_analyses,
                temporal_analysis,
                video_data['metadata']
            )

            # Compile final results
            results = {
                **verdict,
                'num_frames_analyzed': len(video_data['frames']),
                'sampling_strategy': self.sampling_strategy,
                'model_name': self.llm_analyzer.model_name,
                'api_provider': self.api_provider,
                'timestamp': datetime.now().isoformat()
            }

            self.logger.info(f"Detection complete. Classification: {results['classification']}")

            return results

        except Exception as e:
            self.logger.error(f"Detection failed: {str(e)}")
            raise RuntimeError(f"Detection failed: {str(e)}") from e

    def _process_video(self, video_path: str) -> Dict[str, Any]:
        """
        Process video: extract metadata and frames.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with metadata, frames, and timestamps
        """
        processor = VideoProcessor(video_path, num_frames=self.num_frames)
        video_data = processor.process(sampling_strategy=self.sampling_strategy)

        self.logger.debug(f"Extracted {len(video_data['frames'])} frames")
        self.logger.debug(f"Video metadata: {video_data['metadata']}")

        return video_data

    def _analyze_frames(self, frames, metadata) -> list:
        """
        Analyze individual frames for deepfake artifacts.

        Args:
            frames: List of frame images
            metadata: Video metadata

        Returns:
            List of frame analysis results
        """
        frame_analyses = []

        # Analyze a subset of frames to reduce API calls
        # For thorough analysis, analyze first, middle, and last frames
        indices_to_analyze = self._select_key_frames(len(frames))

        for idx in indices_to_analyze:
            self.logger.debug(f"Analyzing frame {idx + 1}/{len(frames)}")

            analysis = self.llm_analyzer.analyze_frame(
                frame=frames[idx],
                frame_index=idx,
                metadata=metadata
            )

            frame_analyses.append(analysis)

        return frame_analyses

    def _select_key_frames(self, total_frames: int, max_frames: int = 5) -> list:
        """
        Select key frames to analyze (to limit API calls).

        Args:
            total_frames: Total number of extracted frames
            max_frames: Maximum frames to analyze in detail

        Returns:
            List of frame indices to analyze
        """
        if total_frames <= max_frames:
            return list(range(total_frames))

        # Select first, last, and evenly distributed middle frames
        indices = [0, total_frames - 1]  # First and last

        # Add middle frames
        step = (total_frames - 2) / (max_frames - 2)
        for i in range(1, max_frames - 1):
            indices.append(int(1 + (i - 1) * step))

        return sorted(list(set(indices)))

    def _analyze_temporal(self, frames, frame_indices) -> Dict[str, Any]:
        """
        Analyze temporal consistency across frames.

        Args:
            frames: List of frame images
            frame_indices: List of frame indices

        Returns:
            Temporal analysis results
        """
        analysis = self.llm_analyzer.analyze_temporal_sequence(
            frames=frames,
            frame_indices=frame_indices
        )

        return analysis

    def _synthesize_verdict(
        self,
        frame_analyses: list,
        temporal_analysis: Dict,
        metadata: Dict
    ) -> Dict[str, Any]:
        """
        Synthesize final verdict from all analyses.

        Args:
            frame_analyses: Frame-level analyses
            temporal_analysis: Temporal analysis
            metadata: Video metadata

        Returns:
            Final verdict dictionary
        """
        verdict = self.llm_analyzer.synthesize_verdict(
            frame_analyses=frame_analyses,
            temporal_analysis=temporal_analysis,
            metadata=metadata
        )

        return verdict

    def detect_and_report(
        self,
        video_path: str,
        output_json: Optional[str] = None,
        output_txt: Optional[str] = None,
        detailed: bool = True
    ) -> Dict[str, Any]:
        """
        Detect deepfake and generate reports.

        Args:
            video_path: Path to video file
            output_json: Optional path to save JSON results
            output_txt: Optional path to save text report
            detailed: Use detailed report format

        Returns:
            Detection results
        """
        # Perform detection
        results = self.detect(video_path)

        # Print to console
        OutputFormatter.print_console_report(results, detailed=detailed)

        # Save JSON if requested
        if output_json:
            OutputFormatter.save_json(results, output_json)
            self.logger.info(f"Saved JSON results to: {output_json}")

        # Save text report if requested
        if output_txt:
            OutputFormatter.save_text_report(results, output_txt, detailed=detailed)
            self.logger.info(f"Saved text report to: {output_txt}")

        return results

    def batch_detect(
        self,
        video_paths: list,
        output_dir: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Perform batch detection on multiple videos.

        Args:
            video_paths: List of video file paths
            output_dir: Optional directory to save results

        Returns:
            Dictionary mapping video paths to results
        """
        results = {}

        for i, video_path in enumerate(video_paths):
            self.logger.info(f"\nProcessing video {i + 1}/{len(video_paths)}: {video_path}")

            try:
                result = self.detect(video_path)
                results[video_path] = result

                # Print summary
                print(OutputFormatter.format_summary(result))

                # Save individual results if output directory specified
                if output_dir:
                    output_path = Path(output_dir)
                    video_name = Path(video_path).stem

                    json_path = output_path / f"{video_name}_analysis.json"
                    OutputFormatter.save_json(result, str(json_path))

            except Exception as e:
                self.logger.error(f"Failed to process {video_path}: {str(e)}")
                results[video_path] = {
                    'error': str(e),
                    'classification': 'ERROR',
                    'confidence': 0
                }

        return results


def create_detector(
    api_provider: str = "anthropic",
    model_name: Optional[str] = None,
    **kwargs
) -> DeepfakeDetector:
    """
    Factory function to create a DeepfakeDetector instance.

    Args:
        api_provider: LLM provider ('anthropic', 'openai', or 'mock')
        model_name: Specific model to use
        **kwargs: Additional arguments passed to DeepfakeDetector

    Returns:
        Configured DeepfakeDetector instance
    """
    return DeepfakeDetector(
        api_provider=api_provider,
        model_name=model_name,
        **kwargs
    )
