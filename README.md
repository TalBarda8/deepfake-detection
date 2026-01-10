# Deepfake Detection System

[![Tests](https://img.shields.io/badge/tests-166%20passed-success)]() [![Coverage](https://img.shields.io/badge/coverage-88.60%25-brightgreen)]() [![Python](https://img.shields.io/badge/python-3.9+-blue)]() [![License](https://img.shields.io/badge/license-MIT-blue)]()

An interpretable deepfake detection system featuring a **self-contained local reasoning agent** that analyzes videos through structured heuristics and transparent analysis, providing detailed explanations without relying on black-box classifiers.

## ✨ Key Features

- **🔍 Local Agent Architecture**: Zero API calls, deterministic results, perfect reproducibility
- **🎯 Interpretable Results**: Detailed explanations with specific visual and temporal evidence
- **⚡ High Performance**: Multiprocessing support for 2-4x speedup on multi-core systems
- **🔌 Extensible Plugin System**: Easy integration of custom frame samplers and analysis hooks
- **📊 Multi-Stage Analysis**: Frame-level visual analysis + temporal consistency checking
- **💰 Zero Cost**: No API usage fees, unlimited offline processing
- **🧩 Modular Design**: Clean architecture with optional external LLM provider support
- **🎓 Academic Grade**: 88.60% test coverage, comprehensive documentation

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/TalBarda8/deepfake-detection.git
cd deepfake-detection

# Setup environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Analyze a video (instant results, no API key needed)
python detect.py --video path/to/video.mp4
```

**Output:**
```
Classification: FAKE
Confidence: 85%
Reasoning: The video exhibits multiple characteristics consistent with
synthetic generation including low texture variance, uniform lighting
patterns, and temporal inconsistencies...
```

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Basic Detection](#basic-detection)
  - [Parallel Processing](#parallel-processing)
  - [Plugin System](#plugin-system)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Prerequisites

- Python 3.9 or higher
- FFmpeg (for video metadata extraction)
- **No API keys required** for local agent (default mode)

### System Setup

**macOS:**
```bash
brew install ffmpeg python@3.9
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg python3.9 python3-pip
```

**Windows:**
- Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
- Install Python 3.9+ from [python.org](https://www.python.org/downloads/)

### Installation

```bash
# Clone repository
git clone https://github.com/TalBarda8/deepfake-detection.git
cd deepfake-detection

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python detect.py --help
```

## 💻 Usage

### Basic Detection

Analyze a video using the local reasoning agent:

```bash
python detect.py --video path/to/video.mp4
```

**Options:**
```bash
python detect.py \
  --video path/to/video.mp4 \
  --frames 15 \                    # Number of frames to analyze
  --sampling uniform \              # Sampling strategy: uniform, adaptive, keyframes
  --output results/analysis.json    # Save results to file
```

### Parallel Processing

Enable multiprocessing for faster analysis on multi-core systems:

```bash
python detect.py \
  --video path/to/video.mp4 \
  --parallel \                      # Enable parallel processing
  --workers 4                       # Number of worker processes
```

**Performance Comparison:**
- Sequential: ~5 seconds for 10 frames
- Parallel (4 workers): ~1.5 seconds for 10 frames
- **Speedup: 2-4x** depending on CPU cores

### Plugin System

Extend functionality with custom plugins:

```python
# plugins/my_sampler.py
from src.plugin_system import FrameSamplerPlugin

class MySampler(FrameSamplerPlugin):
    """Custom frame sampling strategy."""

    def get_name(self) -> str:
        return "my_sampler"

    def sample_frames(self, total_frames: int, num_frames: int) -> list[int]:
        # Your custom sampling logic
        return [0, total_frames//2, total_frames-1]
```

Load and use plugins:

```python
from src.plugin_system import get_plugin_manager

# Auto-discover plugins
pm = get_plugin_manager()
pm.load_plugins_from_directory("plugins")

# Use custom sampler
sampler = pm.get_frame_sampler("my_sampler")
frames = sampler.sample_frames(total_frames=300, num_frames=10)
```

See [`docs/PLUGIN_DEVELOPMENT.md`](docs/PLUGIN_DEVELOPMENT.md) for complete plugin development guide.

### Python API

Use the detector programmatically:

```python
from src.detector import DeepfakeDetector

# Initialize detector
detector = DeepfakeDetector(
    api_provider='local',  # Use local agent (no API calls)
    num_frames=10,
    sampling_strategy='uniform'
)

# Analyze video
result = detector.detect("path/to/video.mp4")

print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidence']}%")
print(f"Reasoning: {result['reasoning']}")
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Entry Point                       │
│                     (detect.py)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Deepfake Detector (Orchestrator)           │
│  - Coordinates analysis pipeline                        │
│  - Manages component interaction                        │
└──────┬─────────────┬──────────────┬─────────────────────┘
       │             │              │
       ▼             ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌──────────────────┐
│   Video     │ │   Local     │ │     Output       │
│  Processor  │ │   Agent     │ │    Formatter     │
└─────────────┘ └─────────────┘ └──────────────────┘
       │             │
       │             │
       ▼             ▼
┌─────────────┐ ┌─────────────┐
│  Parallel   │ │   Plugin    │
│  Processor  │ │   System    │
└─────────────┘ └─────────────┘
```

### Core Modules

| Module | Purpose | Coverage |
|--------|---------|----------|
| `detector.py` | Orchestrates detection pipeline | 88.07% |
| `local_agent.py` | Rule-based reasoning engine | 88.48% |
| `video_processor.py` | Frame extraction & metadata | 100% |
| `parallel_processor.py` | Multiprocessing support | 91.67% |
| `plugin_system.py` | Plugin management | 88.64% |
| `llm_analyzer.py` | Optional LLM integration | 74.25% |
| `output_formatter.py` | Result formatting | 91.80% |

### Detection Pipeline

1. **Video Processing**: Extract frames using configurable sampling strategy
2. **Frame Analysis**: Detect visual artifacts (smoothing, lighting, boundaries)
3. **Temporal Analysis**: Check consistency across frames (motion, transitions)
4. **Verdict Synthesis**: Aggregate evidence and generate classification with confidence

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for detailed architecture documentation including C4 diagrams and Architecture Decision Records (ADRs).

## 📚 API Reference

### DeepfakeDetector

Main detection class for video analysis.

```python
DeepfakeDetector(
    api_provider='local',           # 'local', 'anthropic', or 'openai'
    num_frames=10,                  # Number of frames to analyze
    sampling_strategy='uniform',    # 'uniform', 'adaptive', or 'keyframes'
    parallel=False,                 # Enable parallel processing
    num_workers=None                # Number of workers (default: CPU count)
)
```

**Methods:**

- `detect(video_path: str) -> dict`: Analyze video and return results
- `detect_with_metadata(video_path: str) -> dict`: Include video metadata in results

### VideoProcessor

Frame extraction and metadata handling.

```python
VideoProcessor(
    video_path: str,                # Path to MP4 video
    num_frames: int = 10            # Number of frames to extract
)
```

**Methods:**

- `extract_metadata() -> dict`: Get video metadata (resolution, fps, duration)
- `extract_frames(strategy='uniform') -> list`: Extract frames using sampling strategy
- `get_frame_timestamps() -> list`: Get timestamps for extracted frames

### LocalAgentRunner

Rule-based deepfake detection agent.

```python
LocalAgentRunner(agent_version='v1.0')
```

**Methods:**

- `analyze_frame(frame, frame_index, metadata) -> dict`: Analyze single frame
- `analyze_temporal_sequence(frames, indices) -> dict`: Analyze temporal consistency
- `synthesize_verdict(frame_analyses, temporal_analysis, metadata) -> dict`: Generate final verdict

For complete API documentation, see [`docs/`](docs/) directory.

## 🧪 Testing

Run comprehensive test suite (166 tests):

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report

# Run specific test file
pytest tests/test_local_agent.py -v

# Run parallel processing tests
pytest tests/test_parallel_processor.py -v
```

**Test Coverage:**
- Overall: 88.60%
- 166 tests across 7 test files
- All modules exceed 70% coverage threshold

## 📖 Documentation

Comprehensive documentation available in [`docs/`](docs/):

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System architecture, C4 diagrams, ADRs
- **[BUILDING_BLOCKS.md](docs/BUILDING_BLOCKS.md)**: Detailed component specifications
- **[PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)**: Plugin development guide
- **[COST_ANALYSIS.md](docs/COST_ANALYSIS.md)**: Token usage and cost projections
- **[TESTING.md](docs/TESTING.md)**: Testing strategy and guidelines
- **[PRD.md](docs/PRD.md)**: Product requirements document

**Academic Documentation:**

For assignment-related materials and grading guides, see [`academic/`](academic/) directory:
- `SUBMISSION_READY.md`: Submission checklist
- `GRADING_GUIDE.md`: Comprehensive grading instructions
- `IMPROVEMENT_ROADMAP.md`: Development timeline and improvements

## 🎯 Classification Logic

The local agent uses a multi-stage heuristic approach:

### Visual Artifact Detection

- **Facial Smoothing**: Laplacian variance analysis (threshold: 100-200)
- **Lighting Inconsistency**: Sobel gradient analysis (std threshold: 20)
- **Boundary Artifacts**: Canny edge density analysis (range: 0.05-0.20)
- **Resolution Mismatch**: Frequency domain analysis

### Temporal Consistency

- **Motion Continuity**: Frame-to-frame difference analysis
- **Temporal Artifacts**: Abrupt transition detection
- **Freeze Detection**: Low motion identification

### Confidence Scoring

Combined score: 60% visual artifacts + 40% temporal consistency

- **FAKE** (>0.75): High suspicion score, multiple artifacts
- **LIKELY FAKE** (0.55-0.75): Moderate suspicion, some artifacts
- **UNCERTAIN** (0.45-0.55): Mixed signals, ambiguous evidence
- **LIKELY REAL** (0.25-0.45): Low suspicion, minor issues
- **REAL** (<0.25): Very low suspicion, natural characteristics

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Add tests** for new functionality
4. **Ensure** all tests pass (`pytest`)
5. **Update** documentation as needed
6. **Commit** changes (`git commit -m 'Add amazing feature'`)
7. **Push** to branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/deepfake-detection.git
cd deepfake-detection

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with OpenCV for computer vision processing
- Inspired by research in interpretable AI and deepfake detection
- Supports optional integration with Claude (Anthropic) and GPT-4V (OpenAI)

## 📞 Contact

**Tal Barda** - [@TalBarda8](https://github.com/TalBarda8)

**Project Link**: [https://github.com/TalBarda8/deepfake-detection](https://github.com/TalBarda8/deepfake-detection)

---

**Note**: This system is designed for educational and research purposes. For production deepfake detection, consider specialized models and ensemble approaches.
