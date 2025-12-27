# Product Requirements Document (PRD)
## Deepfake Detection System Using LLM-Based Analysis

**Version:** 1.0
**Date:** December 27, 2025
**Project:** Assignment 09 - Deepfake Detection
**Status:** Planning Phase

---

## 1. Problem Statement

The proliferation of deepfake technology has created significant challenges in determining the authenticity of digital media. Traditional computer vision classifiers often require extensive training data and may not generalize well to novel deepfake generation techniques. Furthermore, they provide limited interpretability regarding *why* a video is classified as fake.

This project addresses the need for an **interpretable, LLM-based video analysis system** that can:
- Identify potential deepfake videos through multi-modal reasoning
- Provide transparent explanations of the analysis process
- Handle uncertainty gracefully (e.g., "likely fake" vs. definitive classifications)
- Serve as an educational tool for understanding deepfake detection principles

The system will be evaluated on its ability to analyze both:
1. A deepfake video generated from a still image using Google Flow (Inframe option)
2. An authentic real video

The focus is on **quality of reasoning and analysis**, not just binary accuracy.

---

## 2. Goals & Non-Goals

### Goals
1. **Primary Goal**: Develop an LLM-based AI agent that analyzes MP4 videos and determines authenticity through reasoned analysis
2. Create a deepfake video from a still image using Google Flow (Inframe option) for testing purposes
3. Implement a system that provides:
   - Classification: Real, Fake, or Uncertain (with confidence levels)
   - Detailed explanation of visual, temporal, and semantic cues
4. Demonstrate the application of prompt engineering and LLM reasoning to video analysis
5. Store all test videos (deepfake and real) within the project repository
6. Provide comprehensive documentation of approach, methodology, and findings

### Non-Goals
1. **NOT** building a traditional computer vision classifier using CNNs, ResNets, or similar architectures
2. **NOT** achieving state-of-the-art binary accuracy metrics (precision/recall optimization)
3. **NOT** creating a production-ready, real-time detection system
4. **NOT** handling video formats other than MP4
5. **NOT** training custom neural networks for feature extraction
6. **NOT** building a user-facing web application or GUI (CLI is sufficient)

---

## 3. System Overview

### Architecture
The system consists of three main components:

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface (CLI)                   │
│                 Input: MP4 video file                    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Video Processing Pipeline                   │
│  - Frame extraction (sampling strategy)                  │
│  - Preprocessing (resolution normalization)              │
│  - Multi-modal encoding (vision + temporal)              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              LLM-Based Analysis Engine                   │
│  - Vision-language model (e.g., GPT-4V, Claude)         │
│  - Prompt engineering for deepfake detection            │
│  - Multi-frame reasoning and temporal analysis          │
│  - Uncertainty quantification                            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Output Generator                      │
│  - Classification: Real/Fake/Uncertain                   │
│  - Confidence score (0-100%)                             │
│  - Detailed reasoning and explanation                    │
│  - Identified suspicious cues or authenticity markers    │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack (Proposed)
- **LLM API**: OpenAI GPT-4V, Anthropic Claude 3.5 Sonnet, or similar vision-capable model
- **Video Processing**: FFmpeg, OpenCV (for frame extraction only)
- **Programming Language**: Python 3.9+
- **Deepfake Generation**: Google Flow (Inframe option)
- **Repository Structure**: Git-based with integrated test videos

---

## 4. User Flow

### Primary Use Case: Video Analysis

1. **User provides input**: Path to MP4 video file
   ```bash
   python detect_deepfake.py --video path/to/video.mp4
   ```

2. **System processes video**:
   - Extracts representative frames (e.g., 5-10 frames evenly distributed)
   - Analyzes video metadata (framerate, resolution, encoding)
   - Prepares frames and metadata for LLM analysis

3. **LLM performs analysis**:
   - Analyzes each frame for visual inconsistencies:
     - Facial features (unnatural blinking, lip sync, lighting)
     - Background artifacts (warping, blurring boundaries)
     - Texture and resolution inconsistencies
   - Performs temporal analysis across frames:
     - Motion continuity
     - Lighting consistency
     - Artifact progression
   - Synthesizes findings into coherent assessment

4. **System generates output**:
   ```
   ====================================
   DEEPFAKE DETECTION ANALYSIS REPORT
   ====================================

   Video: sample_video.mp4
   Classification: LIKELY FAKE
   Confidence: 75%

   ANALYSIS:

   Visual Cues:
   - Unnatural facial smoothing detected in frames 2, 5, 7
   - Inconsistent lighting on face vs. background (frames 3-6)
   - Subtle warping artifacts near jawline (frame 4)

   Temporal Cues:
   - Irregular blinking pattern (blinks at frames 1, 2, inconsistent with natural rhythm)
   - Micro-jitter in facial boundaries suggests generative artifacts

   Semantic Cues:
   - Lip synchronization appears slightly delayed

   CONCLUSION:
   The video exhibits multiple indicators consistent with deepfake generation,
   particularly face-swap or reenactment techniques. The combination of
   facial smoothing, lighting inconsistencies, and temporal artifacts
   suggests synthetic manipulation.

   Recommendation: Treat as potentially manipulated content.
   ====================================
   ```

5. **User reviews findings**: Examines the detailed reasoning to understand the decision

---

## 5. Functional Requirements

### FR1: Video Input Handling
- **FR1.1**: System SHALL accept MP4 video files as input
- **FR1.2**: System SHALL validate video format and reject unsupported formats gracefully
- **FR1.3**: System SHALL handle videos of varying lengths (minimum 1 second, maximum 60 seconds recommended)
- **FR1.4**: System SHALL extract metadata (resolution, framerate, codec, duration)

### FR2: Frame Extraction & Preprocessing
- **FR2.1**: System SHALL extract a representative set of frames (5-15 frames recommended)
- **FR2.2**: System SHALL use a sampling strategy (e.g., uniform sampling, key frame detection)
- **FR2.3**: System SHALL normalize frame resolution if needed for LLM input constraints
- **FR2.4**: System SHALL preserve original aspect ratio during preprocessing

### FR3: LLM-Based Analysis
- **FR3.1**: System SHALL analyze extracted frames using a vision-capable LLM
- **FR3.2**: System SHALL employ prompt engineering to guide analysis toward:
  - Facial feature consistency
  - Lighting and shadow coherence
  - Temporal continuity
  - Background artifacts
  - Texture realism
- **FR3.3**: System SHALL perform multi-frame reasoning (not independent frame analysis)
- **FR3.4**: System SHALL identify specific suspicious cues or authenticity markers

### FR4: Classification & Confidence
- **FR4.1**: System SHALL output one of three classifications:
  - **Real**: Video appears authentic
  - **Fake**: Video appears to be a deepfake
  - **Uncertain**: Insufficient evidence for confident classification
- **FR4.2**: System SHALL provide a confidence score (0-100%)
- **FR4.3**: System MAY provide subcategories (e.g., "Likely Fake", "Highly Suspicious")

### FR5: Explanation Generation
- **FR5.1**: System SHALL generate a detailed textual explanation including:
  - Visual cues identified
  - Temporal inconsistencies
  - Semantic anomalies
  - Reasoning process
- **FR5.2**: Explanations SHALL reference specific frames or time ranges
- **FR5.3**: Explanations SHALL be comprehensible to non-technical users

### FR6: Test Video Requirements
- **FR6.1**: Project repository SHALL include a deepfake video generated using Google Flow (Inframe option)
- **FR6.2**: Project repository SHALL include at least one authentic real video
- **FR6.3**: Videos SHALL be stored in a dedicated `/videos` or `/data/videos` directory
- **FR6.4**: Video metadata (source, generation method) SHALL be documented

### FR7: Output & Reporting
- **FR7.1**: System SHALL output analysis results to console (stdout)
- **FR7.2**: System SHALL optionally save results to a text/JSON file
- **FR7.3**: Output format SHALL be structured and easily parseable

---

## 6. Non-Functional Requirements

### NFR1: Interpretability
- Analysis reasoning MUST be transparent and traceable
- Users should understand *why* a classification was made

### NFR2: Reproducibility
- Given the same video and system version, results should be consistent
- Prompt templates and LLM configurations SHALL be version-controlled
- LLM API version/model SHALL be documented

### NFR3: Performance
- Analysis of a 10-second video SHOULD complete within 60 seconds (excluding API latency)
- Frame extraction SHOULD be optimized to avoid redundant processing

### NFR4: Usability
- System SHALL be operable via command-line interface with clear instructions
- Error messages SHALL be informative and actionable
- Documentation SHALL include usage examples

### NFR5: Extensibility
- Prompt templates SHALL be modular and easily modifiable
- System design SHALL allow swapping LLM providers (OpenAI, Anthropic, etc.)

### NFR6: Academic Integrity
- All code SHALL be original or properly attributed
- LLM usage SHALL be documented transparently
- Methodology SHALL be reproducible from documentation

---

## 7. AI/LLM Approach and Limitations

### Approach

#### Prompt Engineering Strategy
The system will use a multi-stage prompting approach:

1. **Frame-Level Analysis Prompt**:
   - Analyze individual frames for visual artifacts
   - Identify specific anomalies (face morphing, lighting, texture)

2. **Temporal Coherence Prompt**:
   - Compare consecutive frames for consistency
   - Detect unnatural transitions or discontinuities

3. **Synthesis Prompt**:
   - Aggregate findings from all frames
   - Reason about overall authenticity
   - Quantify confidence

#### Example Prompt Template (Conceptual)
```
You are an expert in deepfake detection. Analyze the following video frames
for signs of synthetic manipulation.

Frames: [Frame 1, Frame 2, ..., Frame N]
Metadata: {duration: 5s, resolution: 1920x1080, fps: 30}

Focus on:
1. Facial features: Unnatural smoothing, inconsistent lighting, warping
2. Temporal consistency: Motion continuity, blinking patterns
3. Background: Artifacts, blur boundaries, inconsistencies
4. Overall realism: Does anything appear "too perfect" or "off"?

Provide:
- Classification: Real / Fake / Uncertain
- Confidence: 0-100%
- Detailed reasoning with specific frame references
```

### LLM Selection Criteria
- **Vision capabilities**: Must support image inputs (GPT-4V, Claude 3.5 Sonnet, Gemini Pro Vision)
- **Reasoning quality**: Strong analytical and explanatory capabilities
- **Context window**: Sufficient to process multiple frames + metadata

### Limitations

#### L1: LLM-Specific Limitations
- **Hallucination Risk**: LLMs may "see" artifacts that don't exist or miss subtle ones
- **Inconsistency**: Different runs may produce slightly different analyses
- **Bias**: LLM training data may include biases toward certain deepfake types

#### L2: Technical Limitations
- **Static Frame Analysis**: LLMs analyze frames as images, not continuous video
- **Temporal Reasoning**: Limited compared to specialized video models
- **Subtle Artifacts**: May miss low-level pixel-based artifacts detectable by CNNs

#### L3: Scope Limitations
- **Novel Techniques**: May struggle with cutting-edge deepfake methods not in training data
- **High-Quality Fakes**: State-of-the-art deepfakes may fool LLM-based analysis
- **Context Dependence**: Requires sufficient visual cues; audio analysis not included

#### L4: Practical Limitations
- **API Costs**: LLM API calls can be expensive for batch processing
- **Latency**: Network latency and processing time affect user experience
- **Rate Limits**: API rate limits may constrain throughput

### Mitigation Strategies
- Use multiple frames to increase signal strength
- Employ confidence thresholds ("Uncertain" category)
- Validate against known deepfake/real video pairs
- Document all edge cases and failure modes

---

## 8. Input/Output Definitions

### Input Specification

#### Primary Input: Video File
- **Format**: MP4 (H.264 or H.265 codec)
- **Duration**: 1 second to 60 seconds (recommended)
- **Resolution**: Any (will be normalized if needed)
- **Framerate**: Any (typically 24-60 fps)
- **File Size**: <100 MB recommended
- **Location**: Local filesystem path

#### Command-Line Arguments
```
python detect_deepfake.py [OPTIONS] VIDEO_PATH

Required Arguments:
  VIDEO_PATH              Path to MP4 video file

Optional Arguments:
  --frames N              Number of frames to extract (default: 10)
  --output FILE           Save results to JSON file
  --model MODEL           LLM model to use (default: gpt-4-vision-preview)
  --verbose               Enable detailed logging
  --help                  Show help message
```

### Output Specification

#### Primary Output: Analysis Report (Console)
```
====================================
DEEPFAKE DETECTION ANALYSIS REPORT
====================================

Video: {filename}
Duration: {duration}s
Resolution: {width}x{height}
Frames Analyzed: {num_frames}

Classification: {REAL | FAKE | UNCERTAIN}
Confidence: {confidence}%

ANALYSIS:

Visual Cues:
{detailed visual findings}

Temporal Cues:
{detailed temporal findings}

Semantic Cues:
{detailed semantic findings}

CONCLUSION:
{synthesis and recommendation}

====================================
```

#### Optional Output: JSON File
```json
{
  "video_path": "path/to/video.mp4",
  "metadata": {
    "duration_seconds": 5.2,
    "resolution": "1920x1080",
    "framerate": 30,
    "codec": "h264"
  },
  "analysis": {
    "classification": "FAKE",
    "confidence": 75,
    "visual_cues": [
      "Unnatural facial smoothing in frames 2, 5, 7",
      "Inconsistent lighting on face vs. background"
    ],
    "temporal_cues": [
      "Irregular blinking pattern",
      "Micro-jitter in facial boundaries"
    ],
    "semantic_cues": [
      "Lip synchronization slightly delayed"
    ],
    "conclusion": "Video exhibits multiple indicators consistent with deepfake generation..."
  },
  "model_used": "gpt-4-vision-preview",
  "timestamp": "2025-12-27T17:30:00Z"
}
```

---

## 9. Evaluation Criteria

Success will be measured across multiple dimensions:

### EC1: Technical Implementation (30%)
- **Code Quality**: Clean, well-documented, modular code
- **Functionality**: System performs all required operations without errors
- **Integration**: Successful integration of LLM API and video processing

### EC2: Analysis Quality (40%)
- **Reasoning Depth**: Detailed, specific explanations (not generic statements)
- **Accuracy**: Correct classification of test videos (deepfake and real)
- **Cue Identification**: Specific visual/temporal/semantic cues referenced
- **Uncertainty Handling**: Appropriate use of confidence scores and uncertain classifications

### EC3: Deepfake Generation (10%)
- **Quality**: Successfully generated deepfake using Google Flow (Inframe option)
- **Documentation**: Clear documentation of generation process
- **Integration**: Deepfake video stored in repository and analyzed by system

### EC4: Documentation & Methodology (20%)
- **PRD Completeness**: Comprehensive product requirements document
- **Code Documentation**: Clear README, docstrings, comments
- **Methodology Transparency**: Prompt engineering approach documented
- **Limitations Acknowledged**: Honest assessment of system limitations

### Specific Success Criteria
1. ✅ System correctly identifies deepfake video with confidence >60%
2. ✅ System correctly identifies real video as authentic
3. ✅ Explanations reference specific frames and cues
4. ✅ Analysis includes visual, temporal, and semantic considerations
5. ✅ Code is executable with clear setup instructions
6. ✅ All videos stored in repository
7. ✅ Comprehensive PRD and documentation provided

### Failure Criteria
- ❌ System classifies both videos identically (no discrimination)
- ❌ Explanations are generic and could apply to any video
- ❌ Code does not execute or has critical bugs
- ❌ Missing required documentation (PRD, README)
- ❌ No deepfake video generated or included

---

## 10. Assumptions and Constraints

### Assumptions
1. **LLM API Access**: Assumes access to a vision-capable LLM API (OpenAI, Anthropic, or equivalent)
2. **Video Quality**: Assumes videos are of sufficient resolution (>480p) for analysis
3. **Face Presence**: Assumes videos contain visible human faces (primary target for deepfakes)
4. **Lighting Conditions**: Assumes reasonable lighting (not extremely dark/overexposed)
5. **Academic Use**: Assumes academic/research context with appropriate API usage quotas
6. **English Language**: Assumes any audio/text in videos is in English (if analyzed)

### Constraints

#### Technical Constraints
- **C1**: Must use LLM-based approach (no classical CV classifiers)
- **C2**: Videos must be in MP4 format
- **C3**: Limited to visual analysis (audio analysis out of scope)
- **C4**: Processing time constrained by LLM API latency

#### Resource Constraints
- **C5**: API usage costs must be reasonable for academic assignment
- **C6**: Processing should complete within reasonable time (<5 minutes per video)
- **C7**: Videos must fit within repository size limits (recommend <50 MB each)

#### Scope Constraints
- **C8**: Focus on deepfake detection, not general video quality assessment
- **C9**: No real-time processing required
- **C10**: CLI interface sufficient (no GUI required)

#### Academic Constraints
- **C11**: Must demonstrate understanding of prompt engineering
- **C12**: Must provide transparent methodology
- **C13**: Submission deadline constraints

---

## 11. Project Structure Expectations

The final project repository should follow this structure:

```
deepfake-detection/
│
├── docs/
│   ├── PRD.md                          # This document
│   ├── METHODOLOGY.md                   # Detailed methodology and prompt engineering
│   └── RESULTS.md                       # Analysis results and findings
│
├── src/
│   ├── __init__.py
│   ├── video_processor.py               # Frame extraction and preprocessing
│   ├── llm_analyzer.py                  # LLM API integration and prompting
│   ├── output_formatter.py              # Result formatting and reporting
│   └── utils.py                         # Helper functions
│
├── prompts/
│   ├── frame_analysis.txt               # Frame-level analysis prompt template
│   ├── temporal_analysis.txt            # Temporal coherence prompt template
│   └── synthesis.txt                    # Synthesis prompt template
│
├── videos/
│   ├── deepfake_sample.mp4              # Generated deepfake video
│   ├── real_sample.mp4                  # Authentic real video
│   └── README.md                        # Video metadata and sources
│
├── results/
│   ├── deepfake_sample_analysis.json    # Analysis output for deepfake
│   └── real_sample_analysis.json        # Analysis output for real video
│
├── tests/
│   ├── test_video_processor.py          # Unit tests
│   └── test_llm_analyzer.py             # Integration tests
│
├── detect_deepfake.py                   # Main CLI entry point
├── requirements.txt                     # Python dependencies
├── .env.example                         # Example environment variables (API keys)
├── .gitignore                           # Git ignore file
└── README.md                            # Project overview and usage instructions
```

### Key Files Description

#### `detect_deepfake.py`
Main entry point for the CLI application. Orchestrates video processing, LLM analysis, and output generation.

#### `src/video_processor.py`
Handles video input validation, frame extraction, preprocessing, and metadata extraction.

#### `src/llm_analyzer.py`
Manages LLM API integration, prompt construction, and response parsing.

#### `prompts/*.txt`
Modular prompt templates for different analysis stages. Allows easy experimentation with prompt engineering.

#### `videos/`
Contains test videos with metadata documentation.

#### `results/`
Stores analysis outputs in structured JSON format for reproducibility.

#### `docs/METHODOLOGY.md`
Detailed explanation of:
- Prompt engineering strategies
- LLM selection rationale
- Frame sampling approach
- Analysis pipeline design

#### `docs/RESULTS.md`
Analysis results, observations, and discussion of system performance on test videos.

---

## 12. Development Phases

### Phase 1: Setup & Preparation (Completed)
- ✅ Create PRD
- ✅ Initialize project repository
- ✅ Define project structure

### Phase 2: Deepfake Generation (Next)
- ⏳ Generate deepfake video using Google Flow (Inframe option)
- ⏳ Source and validate real video sample
- ⏳ Store videos in repository with metadata

### Phase 3: Core Development
- ⏳ Implement video processing pipeline
- ⏳ Integrate LLM API (select provider)
- ⏳ Develop prompt templates
- ⏳ Implement frame extraction and sampling

### Phase 4: Analysis Engine
- ⏳ Build LLM-based analysis logic
- ⏳ Implement multi-frame reasoning
- ⏳ Develop confidence scoring mechanism
- ⏳ Create output formatter

### Phase 5: Testing & Refinement
- ⏳ Test on deepfake video
- ⏳ Test on real video
- ⏳ Refine prompts based on results
- ⏳ Document findings

### Phase 6: Documentation & Submission
- ⏳ Complete README with usage instructions
- ⏳ Write METHODOLOGY.md
- ⏳ Write RESULTS.md
- ⏳ Finalize code documentation
- ⏳ Prepare submission

---

## 13. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM API rate limits exceeded | Medium | High | Implement retry logic, use caching |
| LLM misclassifies both videos | Medium | High | Refine prompts, use multiple analysis passes |
| High API costs | Medium | Medium | Optimize frame count, use cost-effective models |
| Poor deepfake generation quality | Low | Medium | Follow Google Flow documentation carefully |
| Insufficient reasoning depth | Medium | High | Engineer detailed prompt templates, provide examples |
| Video format compatibility issues | Low | Low | Validate inputs, provide clear error messages |
| Missing LLM vision capabilities | Low | High | Verify model capabilities before integration |

---

## 14. Success Metrics Summary

**Minimum Viable Success**:
- ✅ System analyzes videos without critical errors
- ✅ Provides classification and explanation for each video
- ✅ Demonstrates LLM-based approach (not classical CV)

**Target Success**:
- ✅ Correctly identifies deepfake with specific cues
- ✅ Correctly identifies real video as authentic
- ✅ Provides detailed, frame-specific reasoning
- ✅ Demonstrates understanding of prompt engineering

**Excellent Success**:
- ✅ All target success criteria
- ✅ Sophisticated multi-stage prompting approach
- ✅ Thoughtful uncertainty handling
- ✅ Comprehensive documentation of methodology
- ✅ Insightful analysis of system limitations
- ✅ Clean, extensible codebase

---

## 15. Glossary

- **Deepfake**: Synthetic media generated using AI, typically involving face-swapping or reenactment
- **LLM**: Large Language Model (e.g., GPT-4, Claude)
- **Vision-capable LLM**: LLM that can process and reason about images/video frames
- **Prompt Engineering**: Crafting input prompts to guide LLM behavior and output quality
- **Frame Extraction**: Sampling still images from video at specific intervals
- **Temporal Analysis**: Examining consistency across time/frames
- **Inframe**: Google Flow option for generating videos from still images
- **Multi-modal Reasoning**: Reasoning that integrates visual, temporal, and semantic information

---

## 16. References & Resources

### Deepfake Generation
- Google Flow (Inframe): [Tool documentation/link to be added]

### LLM APIs
- OpenAI GPT-4V: https://platform.openai.com/docs/guides/vision
- Anthropic Claude 3.5 Sonnet: https://docs.anthropic.com/claude/docs/vision

### Background Research
- Deepfake detection techniques (academic context)
- Prompt engineering best practices
- Video analysis methodologies

---

## Appendix A: Open Questions

1. **Q**: Which LLM provider offers best vision analysis capabilities for this use case?
   - **A**: To be determined during Phase 3 (likely GPT-4V or Claude 3.5 Sonnet)

2. **Q**: Optimal number of frames to extract for analysis?
   - **A**: To be empirically determined (start with 10 frames)

3. **Q**: Should audio analysis be included if video contains speech?
   - **A**: Out of scope for initial version; future enhancement

4. **Q**: How to handle videos without clear faces?
   - **A**: Return "Uncertain" with explanation of analysis limitations

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-27 | Initial Author | Initial PRD creation |

---

**End of Product Requirements Document**
