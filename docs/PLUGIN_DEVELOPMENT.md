# Plugin Development Tutorial

**Version**: 1.0
**Last Updated**: December 30, 2025
**Difficulty**: Intermediate
**Time to Complete**: 30-60 minutes

---

## Table of Contents

1. [Introduction](#introduction)
2. [Plugin System Overview](#plugin-system-overview)
3. [Plugin Types](#plugin-types)
4. [Creating a Frame Sampler Plugin](#creating-a-frame-sampler-plugin)
5. [Creating an Analysis Hook Plugin](#creating-an-analysis-hook-plugin)
6. [Registering and Using Plugins](#registering-and-using-plugins)
7. [Example Plugins](#example-plugins)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

The deepfake detection system provides a **plugin architecture** that allows you to extend functionality without modifying core code. This tutorial will teach you how to:

- Create custom frame sampling strategies
- Hook into the analysis pipeline
- Register and use your plugins
- Follow best practices for plugin development

### Prerequisites

- Python 3.8+
- Basic understanding of the deepfake detection system
- Familiarity with Python classes and protocols

---

## Plugin System Overview

### Architecture

```
┌─────────────────────────────────────────┐
│         PluginManager                   │
│  (Central plugin registry)              │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌─────▼──────┐
    │  Frame  │      │  Analysis  │
    │ Samplers│      │   Hooks    │
    └────┬────┘      └─────┬──────┘
         │                 │
    ┌────▼────────┐   ┌────▼──────────┐
    │ emotion     │   │ scene_logger  │
    │ scene       │   │ custom_hook   │
    │ custom      │   │ ...           │
    └─────────────┘   └───────────────┘
```

### Plugin Types

1. **Frame Sampler Plugins**: Determine which frames to extract from videos
2. **Analysis Hook Plugins**: Execute code before/after frame analysis

---

## Plugin Types

### 1. Frame Sampler Plugin

**Purpose**: Customize frame selection strategy

**Protocol**:
```python
class FrameSamplerPlugin(Protocol):
    name: str          # Unique identifier
    description: str   # Human-readable description

    def sample_frames(
        self,
        total_frames: int,
        num_frames: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """Return list of frame indices to extract."""
        ...
```

**Use Cases**:
- Sample frames based on facial expressions
- Detect scene transitions
- Focus on specific video regions
- Optimize for specific deepfake types

### 2. Analysis Hook Plugin

**Purpose**: Execute custom code during the analysis pipeline

**Protocol**:
```python
class AnalysisHookPlugin(Protocol):
    name: str
    description: str

    def pre_analysis_hook(
        self,
        frames: List[Any],
        metadata: Dict[str, Any]
    ) -> None:
        """Called before frame analysis."""
        ...

    def post_analysis_hook(
        self,
        analyses: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> None:
        """Called after frame analysis."""
        ...
```

**Use Cases**:
- Log analysis progress
- Pre-process frames
- Post-process results
- Generate custom reports
- Integrate with external systems

---

## Creating a Frame Sampler Plugin

### Step 1: Create Plugin File

Create a new Python file in the `plugins/` directory:

**File**: `plugins/my_sampler.py`

```python
"""
My Custom Sampler Plugin

Description of what your sampler does.
"""

from typing import List, Dict, Any, Optional


class MyCustomSampler:
    """
    Brief description of sampling strategy.
    """

    # Required: Unique name for your plugin
    name = "my_sampler"

    # Required: Human-readable description
    description = "My custom frame sampling strategy"

    def sample_frames(
        self,
        total_frames: int,
        num_frames: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Sample frames using custom strategy.

        Args:
            total_frames: Total number of frames in video
            num_frames: Number of frames to sample
            metadata: Optional video metadata (fps, duration, etc.)

        Returns:
            List of frame indices (0-indexed)
        """
        # Your sampling logic here
        indices = []

        # Example: Sample every Nth frame
        step = max(1, total_frames // num_frames)
        for i in range(num_frames):
            frame_idx = min(i * step, total_frames - 1)
            indices.append(frame_idx)

        return indices
```

### Step 2: Implement Sampling Logic

**Example 1: Random Sampling**

```python
import random

def sample_frames(self, total_frames, num_frames, metadata=None):
    """Sample random frames."""
    if total_frames <= num_frames:
        return list(range(total_frames))

    # Random sampling without replacement
    indices = random.sample(range(total_frames), num_frames)
    return sorted(indices)
```

**Example 2: Weighted Sampling (favor beginning/end)**

```python
def sample_frames(self, total_frames, num_frames, metadata=None):
    """Sample with more frames at start/end (where artifacts appear)."""
    if total_frames <= num_frames:
        return list(range(total_frames))

    indices = []

    # 40% from first 20% of video
    start_count = int(num_frames * 0.4)
    start_region = int(total_frames * 0.2)
    step = max(1, start_region // start_count)
    indices.extend(range(0, start_region, step)[:start_count])

    # 20% from middle 60%
    middle_count = int(num_frames * 0.2)
    middle_start = int(total_frames * 0.2)
    middle_end = int(total_frames * 0.8)
    step = max(1, (middle_end - middle_start) // middle_count)
    indices.extend(range(middle_start, middle_end, step)[:middle_count])

    # 40% from last 20%
    end_count = num_frames - len(indices)
    end_start = int(total_frames * 0.8)
    step = max(1, (total_frames - end_start) // end_count)
    indices.extend(range(end_start, total_frames, step)[:end_count])

    return sorted(list(set(indices)))[:num_frames]
```

### Step 3: Test Your Plugin

```python
# Add to bottom of your plugin file
if __name__ == "__main__":
    sampler = MyCustomSampler()

    # Test with 100-frame video, extract 10 frames
    frames = sampler.sample_frames(
        total_frames=100,
        num_frames=10,
        metadata={'fps': 30.0, 'duration': 3.33}
    )

    print(f"Sampled frames: {frames}")
    assert len(frames) == 10, "Should return exactly 10 frames"
    assert all(0 <= f < 100 for f in frames), "All indices should be valid"
    print("✓ Tests passed!")
```

Run test:
```bash
python plugins/my_sampler.py
```

---

## Creating an Analysis Hook Plugin

### Step 1: Create Hook File

**File**: `plugins/my_hook.py`

```python
"""
My Custom Analysis Hook

Description of what your hook does.
"""

from typing import List, Dict, Any
import logging


class MyCustomHook:
    """
    Brief description of hook functionality.
    """

    name = "my_hook"
    description = "My custom analysis hook"

    def __init__(self):
        self.logger = logging.getLogger('MyCustomHook')

    def pre_analysis_hook(
        self,
        frames: List[Any],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Execute before frame analysis.

        Args:
            frames: List of extracted frames (numpy arrays)
            metadata: Video metadata
        """
        self.logger.info(f"Pre-analysis: {len(frames)} frames")

        # Your pre-analysis logic here
        # Examples:
        # - Log video information
        # - Pre-process frames
        # - Initialize state
        # - Validate inputs

    def post_analysis_hook(
        self,
        analyses: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Execute after frame analysis.

        Args:
            analyses: List of analysis results
            metadata: Video metadata
        """
        self.logger.info(f"Post-analysis: {len(analyses)} results")

        # Your post-analysis logic here
        # Examples:
        # - Generate reports
        # - Save to database
        # - Send notifications
        # - Compute statistics
```

### Step 2: Implement Hook Logic

**Example 1: Statistics Logger**

```python
def post_analysis_hook(self, analyses, metadata):
    """Log analysis statistics."""
    suspicion_counts = {
        'LOW': 0,
        'MEDIUM': 0,
        'HIGH': 0
    }

    for analysis in analyses:
        level = analysis.get('suspicion_level', 'UNKNOWN')
        if level in suspicion_counts:
            suspicion_counts[level] += 1

    print("\n" + "="*50)
    print("ANALYSIS STATISTICS")
    print("="*50)
    print(f"Total Frames: {len(analyses)}")
    print(f"Low Suspicion: {suspicion_counts['LOW']}")
    print(f"Medium Suspicion: {suspicion_counts['MEDIUM']}")
    print(f"High Suspicion: {suspicion_counts['HIGH']}")
    print("="*50 + "\n")
```

**Example 2: CSV Export Hook**

```python
import csv
from datetime import datetime

def post_analysis_hook(self, analyses, metadata):
    """Export results to CSV."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_results_{timestamp}.csv"

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['frame_index', 'suspicion_level', 'confidence', 'artifacts']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for analysis in analyses:
            writer.writerow({
                'frame_index': analysis.get('frame_index', 0),
                'suspicion_level': analysis.get('suspicion_level', 'UNKNOWN'),
                'confidence': analysis.get('confidence', 0.0),
                'artifacts': ', '.join(analysis.get('artifacts', []))
            })

    print(f"✓ Exported results to {filename}")
```

---

## Registering and Using Plugins

### Method 1: Manual Registration

```python
from src.plugin_system import get_plugin_manager
from plugins.my_sampler import MyCustomSampler
from plugins.my_hook import MyCustomHook

# Get plugin manager
plugin_manager = get_plugin_manager()

# Register frame sampler
sampler = MyCustomSampler()
plugin_manager.register_frame_sampler(sampler)

# Register analysis hook
hook = MyCustomHook()
plugin_manager.register_analysis_hook(hook)

# Verify registration
print("Registered samplers:", plugin_manager.list_frame_samplers())
print("Registered hooks:", plugin_manager.list_analysis_hooks())
```

### Method 2: Auto-Discovery

Place your plugin files in the `plugins/` directory and use auto-discovery:

```python
from src.plugin_system import get_plugin_manager

# Get plugin manager
plugin_manager = get_plugin_manager(plugins_dir="plugins")

# Auto-discover and load all plugins
loaded_count = plugin_manager.load_plugins_from_directory()
print(f"Loaded {loaded_count} plugins")

# List all plugins
info = plugin_manager.get_plugin_info()
print("Frame Samplers:", info['frame_samplers'])
print("Analysis Hooks:", info['analysis_hooks'])
```

### Using a Frame Sampler

```python
from src.plugin_system import get_plugin_manager
from src.video_processor import VideoProcessor

# Get plugin manager and load plugins
plugin_manager = get_plugin_manager()
plugin_manager.load_plugins_from_directory()

# Get your custom sampler
sampler = plugin_manager.get_frame_sampler('my_sampler')

if sampler:
    # Use sampler to get frame indices
    indices = sampler.sample_frames(
        total_frames=150,
        num_frames=10,
        metadata={'fps': 30.0, 'duration': 5.0}
    )

    print(f"Sampled frames: {indices}")

    # Now extract those specific frames
    # (You would integrate this with VideoProcessor)
```

### Using Analysis Hooks

```python
from src.plugin_system import get_plugin_manager

# Get plugin manager
plugin_manager = get_plugin_manager()
plugin_manager.load_plugins_from_directory()

# Hooks are executed automatically during analysis
# Pre-analysis hooks
plugin_manager.execute_pre_analysis_hooks(
    frames=extracted_frames,
    metadata=video_metadata
)

# ... perform analysis ...

# Post-analysis hooks
plugin_manager.execute_post_analysis_hooks(
    analyses=analysis_results,
    metadata=video_metadata
)
```

---

## Example Plugins

### Example 1: Emotion-Based Sampler

**File**: `plugins/emotion_sampler.py`

Samples frames at likely emotional transition points (beginning, middle, end, transitions).

**Usage**:
```python
from plugins.emotion_sampler import EmotionBasedSampler

sampler = EmotionBasedSampler()
frames = sampler.sample_frames(total_frames=300, num_frames=15)
# Returns: [15, 45, 105, 150, 195, 255, 285, ...]
```

**Strategy**: 40% from start, 20% from middle, 40% from end (where emotions change)

### Example 2: Scene-Based Sampler

**File**: `plugins/scene_sampler.py`

Samples frames at likely scene transitions (every ~3 seconds).

**Usage**:
```python
from plugins.scene_sampler import SceneBasedSampler

sampler = SceneBasedSampler()
frames = sampler.sample_frames(
    total_frames=450,
    num_frames=20,
    metadata={'fps': 30.0, 'duration': 15.0}
)
# Returns frames at scene boundaries
```

**Strategy**: Divides video into scenes, samples at boundaries (where artifacts appear)

### Example 3: Scene Transition Hook

**File**: `plugins/scene_sampler.py` (SceneTransitionHook)

Logs detected scene transitions during analysis.

**Usage**:
```python
from plugins.scene_sampler import SceneTransitionHook

hook = SceneTransitionHook()

# Hooks execute automatically when registered
# Output example:
# [SceneTransitionHook] Detected 3 potential scene transitions:
#   Frame 10 → 20: LOW → HIGH
#   Frame 40 → 50: HIGH → LOW
#   Frame 80 → 90: LOW → MEDIUM
```

---

## Best Practices

### 1. Naming Conventions

- **Plugin names**: Use lowercase with underscores (e.g., `emotion_sampler`)
- **File names**: Match plugin name (e.g., `emotion_sampler.py`)
- **Class names**: Use PascalCase (e.g., `EmotionBasedSampler`)

### 2. Documentation

Always include:
- Docstrings for classes and methods
- Description of sampling/hook strategy
- Example usage in `if __name__ == "__main__"` block

```python
"""
Plugin Name

Detailed description of what the plugin does and when to use it.
"""

class MyPlugin:
    """Brief class description."""

    def method(self, param):
        """
        Method description.

        Args:
            param: Parameter description

        Returns:
            Return value description
        """
        pass
```

### 3. Error Handling

Handle errors gracefully:

```python
def sample_frames(self, total_frames, num_frames, metadata=None):
    """Sample frames with error handling."""
    try:
        # Validate inputs
        if total_frames <= 0:
            raise ValueError("total_frames must be positive")
        if num_frames <= 0:
            raise ValueError("num_frames must be positive")

        # Your logic here
        indices = [...]

        # Validate outputs
        if len(indices) != num_frames:
            self.logger.warning(
                f"Expected {num_frames} frames, got {len(indices)}"
            )

        return indices

    except Exception as e:
        self.logger.error(f"Sampling failed: {e}")
        # Fallback to uniform sampling
        step = max(1, total_frames // num_frames)
        return [i * step for i in range(num_frames)]
```

### 4. Testing

Test your plugins thoroughly:

```python
def test_sampler():
    """Test custom sampler."""
    sampler = MyCustomSampler()

    # Test normal case
    frames = sampler.sample_frames(100, 10)
    assert len(frames) == 10
    assert all(0 <= f < 100 for f in frames)

    # Test edge cases
    frames = sampler.sample_frames(5, 10)  # Fewer frames than requested
    assert len(frames) == 5

    frames = sampler.sample_frames(100, 1)  # Single frame
    assert len(frames) == 1

    print("✓ All tests passed!")

if __name__ == "__main__":
    test_sampler()
```

### 5. Performance

Consider performance for large videos:

```python
def sample_frames(self, total_frames, num_frames, metadata=None):
    """Efficient sampling for large videos."""
    # Use generator for memory efficiency
    # Use simple math instead of complex algorithms
    # Avoid loading entire video into memory

    step = total_frames / num_frames
    indices = [int(i * step) for i in range(num_frames)]
    return indices
```

---

## Troubleshooting

### Plugin Not Found

**Problem**: Plugin not discovered by auto-discovery

**Solutions**:
1. Ensure plugin file is in `plugins/` directory
2. Check that plugin class has required attributes (`name`, `sample_frames` or hooks)
3. Verify no syntax errors in plugin file

```bash
# Test plugin file directly
python plugins/my_sampler.py
```

### Import Errors

**Problem**: `ModuleNotFoundError` when loading plugin

**Solutions**:
1. Install required dependencies
2. Check Python path includes project root
3. Use relative imports within plugins

```python
# Add to top of plugin file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Hook Not Executing

**Problem**: Hook registered but not being called

**Solutions**:
1. Verify hook has correct method names (`pre_analysis_hook`, `post_analysis_hook`)
2. Check that hook is registered before analysis runs
3. Enable debug logging to see hook execution

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Incorrect Frame Indices

**Problem**: Sampler returns invalid indices (negative, too large, etc.)

**Solutions**:
1. Validate inputs at start of method
2. Clamp indices to valid range
3. Remove duplicates and sort

```python
def sample_frames(self, total_frames, num_frames, metadata=None):
    """Sample with validation."""
    # ... sampling logic ...

    # Validate and clean indices
    indices = sorted(list(set(indices)))  # Remove duplicates, sort
    indices = [max(0, min(i, total_frames - 1)) for i in indices]  # Clamp
    return indices[:num_frames]  # Trim to exact count
```

---

## Advanced Topics

### Accessing Video Metadata

```python
def sample_frames(self, total_frames, num_frames, metadata=None):
    """Use metadata for intelligent sampling."""
    if metadata:
        fps = metadata.get('fps', 30.0)
        duration = metadata.get('duration', total_frames / fps)

        # Sample based on time instead of frames
        time_step = duration / num_frames
        indices = [int(i * time_step * fps) for i in range(num_frames)]
        return indices
    else:
        # Fallback if no metadata
        return uniform_sampling(total_frames, num_frames)
```

### Stateful Hooks

```python
class StatefulHook:
    """Hook that maintains state across calls."""

    name = "stateful_hook"
    description = "Maintains analysis state"

    def __init__(self):
        self.analysis_count = 0
        self.total_frames_analyzed = 0

    def pre_analysis_hook(self, frames, metadata):
        """Track analysis."""
        self.analysis_count += 1
        self.total_frames_analyzed += len(frames)
        print(f"Analysis #{self.analysis_count}: {len(frames)} frames")

    def post_analysis_hook(self, analyses, metadata):
        """Report statistics."""
        print(f"Total analyses: {self.analysis_count}")
        print(f"Total frames: {self.total_frames_analyzed}")
```

### Combining Multiple Plugins

```python
# Use multiple samplers for ensemble sampling
sampler1 = EmotionBasedSampler()
sampler2 = SceneBasedSampler()

frames1 = sampler1.sample_frames(300, 10)
frames2 = sampler2.sample_frames(300, 10)

# Combine and remove duplicates
combined_frames = sorted(list(set(frames1 + frames2)))
print(f"Ensemble sampled {len(combined_frames)} unique frames")
```

---

## Summary

You've learned how to:

- ✅ Understand the plugin system architecture
- ✅ Create frame sampler plugins
- ✅ Create analysis hook plugins
- ✅ Register and use plugins
- ✅ Follow best practices
- ✅ Troubleshoot common issues

### Next Steps

1. **Create your own plugin**: Start with a simple frame sampler
2. **Test thoroughly**: Use the testing patterns shown
3. **Share your plugin**: Contribute to the community
4. **Explore examples**: Study the built-in plugins (`emotion_sampler.py`, `scene_sampler.py`)

### Resources

- **Source Code**: `src/plugin_system.py`
- **Examples**: `plugins/emotion_sampler.py`, `plugins/scene_sampler.py`
- **API Documentation**: `docs/BUILDING_BLOCKS.md`
- **Architecture**: `docs/ARCHITECTURE.md`

---

**Happy Plugin Development!** 🎉
