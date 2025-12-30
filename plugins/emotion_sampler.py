"""
Emotion-Based Frame Sampler Plugin

Samples frames with emphasis on regions where facial expressions/emotions
are likely to change, which can reveal deepfake artifacts.
"""

from typing import List, Dict, Any, Optional
import random


class EmotionBasedSampler:
    """
    Frame sampler that emphasizes frames with potential emotional transitions.

    This sampler is designed for deepfake detection where emotional transitions
    often reveal artifacts (inconsistent facial expressions, unnatural movements).

    Strategy:
    - Sample more densely at the beginning, middle, and end of the video
    - These are typical transition points for emotions
    - Deepfakes often have artifacts during expression changes
    """

    name = "emotion"
    description = "Samples frames at likely emotional transition points"

    def sample_frames(
        self,
        total_frames: int,
        num_frames: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Sample frames with emphasis on emotional transition points.

        Args:
            total_frames: Total number of frames in video
            num_frames: Number of frames to sample
            metadata: Optional video metadata

        Returns:
            List of frame indices to extract
        """
        if total_frames <= num_frames:
            return list(range(total_frames))

        # Divide video into segments for emotional transitions
        # Start (0-15%): Initial expression
        # Transitions (15%, 35%, 55%, 75%): Likely emotion changes
        # End (85-100%): Final expression

        transition_points = [
            0.05,   # 5% - Beginning
            0.15,   # 15% - Early transition
            0.35,   # 35% - First major transition
            0.50,   # 50% - Middle (often peak emotion)
            0.65,   # 65% - Second major transition
            0.85,   # 85% - Late transition
            0.95    # 95% - End
        ]

        # Allocate frames to transition points
        base_frames_per_point = num_frames // len(transition_points)
        remaining_frames = num_frames % len(transition_points)

        indices = []

        for i, point in enumerate(transition_points):
            # Calculate center frame for this transition point
            center_frame = int(total_frames * point)

            # Add extra frames to first few points if there are remaining frames
            frames_at_point = base_frames_per_point
            if i < remaining_frames:
                frames_at_point += 1

            # Sample frames around the transition point
            if frames_at_point == 1:
                indices.append(center_frame)
            else:
                # Spread frames around the transition point
                spread = min(total_frames // 20, 10)  # Max 10 frame spread
                for j in range(frames_at_point):
                    offset = int((j - frames_at_point / 2) * spread)
                    frame_idx = max(0, min(total_frames - 1, center_frame + offset))
                    indices.append(frame_idx)

        # Remove duplicates and sort
        indices = sorted(list(set(indices)))

        # If we have too many frames, trim to exact count
        if len(indices) > num_frames:
            # Keep evenly distributed subset
            step = len(indices) / num_frames
            indices = [indices[int(i * step)] for i in range(num_frames)]

        # If we have too few, add random frames in between
        while len(indices) < num_frames:
            # Find largest gap and add frame in middle
            gaps = [(indices[i+1] - indices[i], i) for i in range(len(indices) - 1)]
            if gaps:
                largest_gap, gap_idx = max(gaps)
                new_frame = (indices[gap_idx] + indices[gap_idx + 1]) // 2
                indices.insert(gap_idx + 1, new_frame)
            else:
                break

        return sorted(indices[:num_frames])


# Example usage for testing:
if __name__ == "__main__":
    sampler = EmotionBasedSampler()
    print(f"Plugin: {sampler.name}")
    print(f"Description: {sampler.description}")

    # Test with 100-frame video, extracting 10 frames
    frames = sampler.sample_frames(total_frames=100, num_frames=10)
    print(f"\nSampled frames: {frames}")
    print(f"Total sampled: {len(frames)}")
