"""
Scene-Based Frame Sampler Plugin

Samples frames at likely scene transitions, where deepfake artifacts
are more likely to be visible due to changes in lighting, perspective, etc.
"""

from typing import List, Dict, Any, Optional
import math


class SceneBasedSampler:
    """
    Frame sampler that emphasizes frames at likely scene transitions.

    This sampler is designed for deepfake detection where scene transitions
    often reveal artifacts (lighting inconsistencies, quality changes, etc.).

    Strategy:
    - Divide video into equal segments (scenes)
    - Sample frames at the beginning and end of each scene
    - Scene boundaries are where deepfakes often have quality drops
    """

    name = "scene"
    description = "Samples frames at likely scene transition boundaries"

    def sample_frames(
        self,
        total_frames: int,
        num_frames: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Sample frames at scene transition boundaries.

        Args:
            total_frames: Total number of frames in video
            num_frames: Number of frames to sample
            metadata: Optional video metadata

        Returns:
            List of frame indices to extract
        """
        if total_frames <= num_frames:
            return list(range(total_frames))

        # Estimate number of scenes based on video length
        # Typical scene length: 2-5 seconds
        fps = metadata.get('fps', 30.0) if metadata else 30.0
        duration = metadata.get('duration', total_frames / fps) if metadata else total_frames / fps

        # Estimate scene count (assume average 3-second scenes)
        estimated_scene_count = max(2, int(duration / 3))

        # Adjust scene count to match frame budget
        # We want 2 frames per scene (start and end)
        max_scenes = num_frames // 2
        scene_count = min(estimated_scene_count, max_scenes)

        # Calculate scene boundaries
        scene_length = total_frames / scene_count

        indices = []

        for scene_idx in range(scene_count):
            scene_start = int(scene_idx * scene_length)
            scene_end = int((scene_idx + 1) * scene_length) - 1

            # Sample at scene boundaries
            # Start of scene (captures new lighting/perspective)
            start_offset = min(5, int(scene_length * 0.05))  # First 5% of scene
            indices.append(min(scene_start + start_offset, total_frames - 1))

            # End of scene (captures transition artifacts)
            if len(indices) < num_frames:
                end_offset = min(5, int(scene_length * 0.05))
                indices.append(max(0, min(scene_end - end_offset, total_frames - 1)))

        # Add middle frames if we need more
        if len(indices) < num_frames:
            # Add frames at scene midpoints
            for scene_idx in range(scene_count):
                if len(indices) >= num_frames:
                    break

                scene_start = int(scene_idx * scene_length)
                scene_end = int((scene_idx + 1) * scene_length)
                scene_middle = (scene_start + scene_end) // 2

                if scene_middle not in indices:
                    indices.append(scene_middle)

        # Fill remaining with uniform sampling if still not enough
        if len(indices) < num_frames:
            uniform_indices = []
            step = total_frames / num_frames
            for i in range(num_frames):
                frame_idx = int(i * step)
                if frame_idx not in indices:
                    uniform_indices.append(frame_idx)

            # Add uniform indices until we reach num_frames
            indices.extend(uniform_indices[:num_frames - len(indices)])

        # Remove duplicates and sort
        indices = sorted(list(set(indices)))

        # Trim to exact count if needed
        if len(indices) > num_frames:
            # Keep evenly distributed subset
            step = len(indices) / num_frames
            indices = [indices[int(i * step)] for i in range(num_frames)]

        return sorted(indices[:num_frames])


class SceneTransitionHook:
    """
    Analysis hook that logs scene transition information.

    This hook analyzes frame transitions to identify potential scene changes
    and logs them for further investigation.
    """

    name = "scene_transition_logger"
    description = "Logs detected scene transitions during analysis"

    def pre_analysis_hook(
        self,
        frames: List[Any],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Log scene transition detection before analysis.

        Args:
            frames: List of extracted frames
            metadata: Video metadata
        """
        print(f"[SceneTransitionHook] Analyzing {len(frames)} frames for scene transitions")

    def post_analysis_hook(
        self,
        analyses: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Log scene transitions detected during analysis.

        Args:
            analyses: List of analysis results
            metadata: Video metadata
        """
        # Detect potential scene transitions based on suspicion level changes
        transitions = []

        for i in range(len(analyses) - 1):
            current = analyses[i]
            next_frame = analyses[i + 1]

            # Check if suspicion level changed significantly
            if current.get('suspicion_level') != next_frame.get('suspicion_level'):
                transitions.append({
                    'from_frame': current.get('frame_index', i),
                    'to_frame': next_frame.get('frame_index', i + 1),
                    'from_suspicion': current.get('suspicion_level', 'UNKNOWN'),
                    'to_suspicion': next_frame.get('suspicion_level', 'UNKNOWN')
                })

        if transitions:
            print(f"\n[SceneTransitionHook] Detected {len(transitions)} potential scene transitions:")
            for t in transitions:
                print(f"  Frame {t['from_frame']} → {t['to_frame']}: "
                      f"{t['from_suspicion']} → {t['to_suspicion']}")
        else:
            print(f"[SceneTransitionHook] No significant scene transitions detected")


# Example usage for testing:
if __name__ == "__main__":
    sampler = SceneBasedSampler()
    print(f"Plugin: {sampler.name}")
    print(f"Description: {sampler.description}")

    # Test with 150-frame video (5 seconds at 30fps), extracting 10 frames
    frames = sampler.sample_frames(
        total_frames=150,
        num_frames=10,
        metadata={'fps': 30.0, 'duration': 5.0}
    )
    print(f"\nSampled frames: {frames}")
    print(f"Total sampled: {len(frames)}")

    # Test hook
    print("\n" + "="*50)
    hook = SceneTransitionHook()
    print(f"Hook: {hook.name}")
    print(f"Description: {hook.description}")
