# Deepfake Detection System - LLM-Based Analysis

An interpretable deepfake detection system that uses vision-capable Large Language Models (LLMs) to analyze videos through reasoning and prompt engineering, rather than traditional computer vision classifiers.

**Project:** Assignment 09 - Deepfake Detection
**Approach:** LLM-based reasoning with focus on interpretability and explanation quality

## Overview

This system analyzes MP4 videos to determine authenticity using multi-modal LLM analysis. Instead of relying on pretrained classifiers, it uses structured prompt engineering to guide vision-capable LLMs in identifying visual, temporal, and semantic artifacts characteristic of deepfake videos.

### Key Features

- **LLM-Based Reasoning**: Uses Claude 3.5 Sonnet or GPT-4V for intelligent video analysis
- **Interpretable Results**: Provides detailed explanations, not just binary classifications
- **Multi-Stage Analysis**: Combines frame-level visual analysis with temporal consistency checks
- **Uncertainty Handling**: Explicitly handles uncertain cases with confidence scores
- **No Training Required**: Pure prompt engineering approach, no model training
- **Modular Design**: Clean, extensible architecture

### Classification Categories

- **REAL**: High confidence the video is authentic
- **LIKELY REAL**: Moderate confidence, minor ambiguities
- **UNCERTAIN**: Insufficient evidence for confident determination
- **LIKELY FAKE**: Moderate confidence the video is synthetic
- **FAKE**: High confidence the video is a deepfake

## Installation

### Prerequisites

- Python 3.9 or higher
- FFmpeg (for video processing)
- API key for Anthropic (Claude) or OpenAI (GPT-4)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/TalBarda8/deepfake-detection.git
   cd deepfake-detection
   ```

2. **Install FFmpeg** (if not already installed):
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure API keys**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

## Usage

### Basic Usage

Analyze a single video:

```bash
python detect.py --video data/videos/fake/deepfake_inframe_v1.mp4
```

### Advanced Options

```bash
# Use specific model
python detect.py --video video.mp4 --provider openai --model gpt-4o

# Extract more frames for detailed analysis
python detect.py --video video.mp4 --frames 15

# Save results to files
python detect.py --video video.mp4 --output results.json --output-txt report.txt

# Use adaptive frame sampling
python detect.py --video video.mp4 --sampling adaptive

# Detailed output
python detect.py --video video.mp4 --detailed

# Testing mode without API calls
python detect.py --video video.mp4 --provider mock
```

### Batch Processing

Analyze multiple videos:

```bash
# Process all videos in a directory
python detect.py --batch data/videos/fake/*.mp4 --output-dir results/

# Process specific files
python detect.py --batch video1.mp4 video2.mp4 video3.mp4 --output-dir results/
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--video` | Path to video file | Required* |
| `--batch` | Paths to multiple videos | Required* |
| `--output` | Save JSON results to file | None |
| `--output-txt` | Save text report to file | None |
| `--output-dir` | Directory for batch results | None |
| `--provider` | LLM provider (anthropic/openai/mock) | anthropic |
| `--model` | Specific model name | Provider default |
| `--frames` | Number of frames to extract | 10 |
| `--sampling` | Sampling strategy (uniform/adaptive) | uniform |
| `--detailed` | Show detailed report | False |
| `--verbose` | Enable verbose logging | False |
| `--quiet` | Suppress console output | False |

*One of `--video` or `--batch` is required

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                CLI Interface (detect.py)             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│          Detector (src/detector.py)                  │
│  - Orchestrates detection pipeline                   │
│  - Coordinates modules                               │
└────┬───────────────┬────────────────────┬───────────┘
     │               │                    │
     ▼               ▼                    ▼
┌──────────┐  ┌──────────────┐  ┌─────────────────┐
│  Video   │  │     LLM      │  │     Output      │
│Processor │  │   Analyzer   │  │   Formatter     │
│          │  │              │  │                 │
│- Extract │  │- Frame anal. │  │- Console report │
│  metadata│  │- Temporal    │  │- JSON export    │
│- Sample  │  │  analysis    │  │- Text report    │
│  frames  │  │- Synthesis   │  │                 │
└──────────┘  └──────────────┘  └─────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │   Prompts   │
              │  Templates  │
              └─────────────┘
```

### Core Modules

1. **video_processor.py**: Video loading, frame extraction, metadata extraction
2. **llm_analyzer.py**: LLM API integration, prompt construction, analysis
3. **detector.py**: Main orchestration, pipeline coordination
4. **output_formatter.py**: Result formatting and reporting

### Prompt Templates

Located in `prompts/`:
- `frame_analysis.txt`: Frame-level visual artifact detection
- `temporal_analysis.txt`: Temporal consistency analysis
- `synthesis.txt`: Final verdict synthesis

## Analysis Pipeline

### Step 1: Video Processing
- Validate video file
- Extract metadata (resolution, duration, codec, fps)
- Sample frames using specified strategy

### Step 2: Frame-Level Analysis
- Analyze individual frames for visual artifacts:
  - Facial smoothing and texture
  - Lighting inconsistencies
  - Boundary warping
  - Resolution mismatches

### Step 3: Temporal Analysis
- Compare frames for temporal consistency:
  - Motion continuity
  - Blinking patterns
  - Lighting stability
  - Boundary flickering

### Step 4: Synthesis
- Aggregate all evidence
- Determine classification and confidence
- Generate detailed reasoning

## Example Output

```
======================================================================
DEEPFAKE DETECTION ANALYSIS REPORT
======================================================================

Video: deepfake_inframe_v1.mp4
Duration: 5.20s
Resolution: 1920x1080
Frames Analyzed: 10

Classification: LIKELY FAKE
Confidence: 75%

ANALYSIS:

Classification: LIKELY FAKE
Confidence: 75%

KEY EVIDENCE:
- Unnatural facial smoothing observed in frames 2, 5, and 7
- Lighting inconsistency between face and background in multiple frames
- Temporal artifacts: subtle warping at face boundaries between frames 3-4
- Blinking pattern appears irregular (frames 1, 2)

REASONING:
The video exhibits several characteristics consistent with deepfake generation.
The most significant indicator is the unnatural facial texture smoothing visible
in multiple frames, which suggests synthetic face generation or enhancement.
Additionally, the lighting on the subject's face does not fully match the
environmental lighting in the background, suggesting these elements may have
been composited rather than captured together.

Temporal analysis reveals subtle morphing artifacts at face boundaries,
particularly visible during head movements. While these artifacts are not
severe, they are consistent with face-swapping or reenactment techniques.

The combination of visual and temporal artifacts provides moderate to high
confidence that this video is synthetically generated.

UNCERTAINTY FACTORS:
The overall quality is relatively high, and some artifacts could potentially
be attributed to video compression. However, the pattern and consistency of
artifacts across multiple frames suggests synthetic generation rather than
compression alone.

RECOMMENDATION:
Treat as potentially manipulated content. The video shows multiple indicators
of synthetic generation with moderate to high confidence.

======================================================================
Analysis completed at: 2025-12-27 18:30:45
======================================================================
```

## Project Structure

```
deepfake-detection/
├── src/
│   ├── __init__.py
│   ├── video_processor.py      # Video processing and frame extraction
│   ├── llm_analyzer.py          # LLM integration and analysis
│   ├── detector.py              # Main detection orchestration
│   └── output_formatter.py      # Result formatting
├── prompts/
│   ├── frame_analysis.txt       # Frame-level analysis prompt
│   ├── temporal_analysis.txt    # Temporal analysis prompt
│   └── synthesis.txt            # Synthesis prompt
├── data/
│   └── videos/
│       ├── fake/                # Deepfake test videos
│       └── real/                # Authentic test videos
├── docs/
│   ├── PRD.md                   # Product Requirements Document
│   ├── deepfake_generation.md   # Deepfake generation documentation
│   ├── detection_agent.md       # Detection system documentation
│   └── PHASE2_COMPLETION_GUIDE.md
├── results/                     # Analysis results (optional)
├── detect.py                    # Main CLI entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore patterns
└── README.md                    # This file
```

## Documentation

- **[PRD.md](docs/PRD.md)**: Complete product requirements and specifications
- **[detection_agent.md](docs/detection_agent.md)**: Detailed system architecture and design decisions
- **[deepfake_generation.md](docs/deepfake_generation.md)**: Deepfake video generation process

## Methodology

### LLM-Based Approach

This system uses **prompt engineering** to guide vision-capable LLMs in analyzing videos:

1. **No Training**: System uses pretrained vision-language models without fine-tuning
2. **Reasoning Over Classification**: LLMs analyze and explain rather than just classify
3. **Multi-Stage Analysis**: Separate prompts for visual, temporal, and synthesis stages
4. **Explicit Instructions**: Detailed prompts guide the LLM to look for specific artifacts

### Prompt Engineering Strategy

Prompts are designed to:
- Guide attention to specific artifact types (smoothing, lighting, warping)
- Request structured analysis with concrete observations
- Encourage uncertainty acknowledgment
- Distinguish between compression and manipulation artifacts

### Known Limitations

1. **LLM Limitations**:
   - May hallucinate artifacts that don't exist
   - Limited to static frame analysis (not true video understanding)
   - Results may vary between runs

2. **Technical Limitations**:
   - Cannot detect all deepfake types, especially high-quality ones
   - Relies on visible artifacts; may miss subtle manipulations
   - No audio analysis included

3. **Scope Limitations**:
   - Designed for educational/research purposes
   - Not suitable for production deployment
   - Requires API access and incurs costs

For detailed discussion of limitations, see [detection_agent.md](docs/detection_agent.md).

## Testing

### Mock Mode

Test the system without API calls:

```bash
python detect.py --video video.mp4 --provider mock
```

Mock mode returns simulated analysis results for testing the pipeline.

### Validation

Test on provided videos:

```bash
# Test on deepfake video
python detect.py --video data/videos/fake/deepfake_inframe_v1.mp4

# Test on real video
python detect.py --video data/videos/real/real_video_v1.mp4
```

## API Costs

**Important**: This system makes LLM API calls which incur costs.

Approximate costs per video (10 frames):
- **Anthropic Claude 3.5 Sonnet**: ~$0.10-0.30 per video
- **OpenAI GPT-4V**: ~$0.15-0.40 per video

To minimize costs:
- Use fewer frames (`--frames 5`)
- Use mock mode for testing (`--provider mock`)
- Process videos selectively

## Academic Context

This project is developed for **Assignment 09: Deepfake Detection** with focus on:
- **Interpretability**: Understanding *why* a video is classified as fake
- **Reasoning Quality**: Detailed, specific explanations over raw accuracy
- **Educational Value**: Demonstrating LLM capabilities in video analysis
- **Methodology Transparency**: Reproducible prompt engineering approach

## Ethics and Responsible Use

This tool is developed for:
- Academic research and education
- Understanding deepfake detection methodologies
- Demonstrating LLM-based analysis techniques

**This tool should NOT be used for**:
- Generating deepfakes for malicious purposes
- Automated decision-making without human review
- Legal or forensic evidence without expert validation

The deepfake videos included are for testing purposes only and are clearly labeled.

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'cv2'`
**Solution**: Install OpenCV: `pip install opencv-python`

**Issue**: `ffprobe: command not found`
**Solution**: Install FFmpeg (see Installation section)

**Issue**: `Error: API key not found`
**Solution**: Create `.env` file with your API keys (see Setup Steps)

**Issue**: API rate limits exceeded
**Solution**: Reduce number of frames (`--frames 5`) or wait before retrying

**Issue**: Out of memory errors
**Solution**: Reduce frame count or video resolution

### Getting Help

For issues or questions:
1. Check the [detection_agent.md](docs/detection_agent.md) documentation
2. Review the [PRD.md](docs/PRD.md) for system specifications
3. Check logs with `--verbose` flag for debugging

## Contributing

This is an academic project. For improvements or extensions:
1. Follow the modular architecture
2. Document changes in appropriate files
3. Update prompts with version comments
4. Test with both mock and real APIs

## License

This project is developed for academic purposes. Code is provided as-is for educational use.

## Acknowledgments

- Assignment 09: Deepfake Detection
- LLM providers: Anthropic (Claude), OpenAI (GPT-4)
- Video processing: FFmpeg, OpenCV

---

**Version**: 1.0.0
**Last Updated**: December 27, 2025
**Status**: Phase 3 Complete - Detection System Implemented
