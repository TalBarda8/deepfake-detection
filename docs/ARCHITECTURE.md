# System Architecture Documentation

**Project:** Deepfake Detection System
**Version:** 2.0.0
**Last Updated:** December 29, 2025
**Author:** Tal Barda

## Table of Contents

1. [Overview](#overview)
2. [C4 Model Diagrams](#c4-model-diagrams)
3. [Component Interactions](#component-interactions)
4. [Data Flow](#data-flow)
5. [Deployment Architecture](#deployment-architecture)
6. [Architecture Decision Records](#architecture-decision-records)

---

## Overview

The Deepfake Detection System is designed with a modular, layered architecture that prioritizes:
- **Reproducibility**: Deterministic outputs for academic evaluation
- **Extensibility**: Easy integration of new analysis providers
- **Maintainability**: Clear separation of concerns
- **Testability**: Independent component testing

### Architecture Style

**Layered Architecture** with **Strategy Pattern** for analysis providers:
- **Presentation Layer**: CLI interface (`detect.py`)
- **Application Layer**: Detection orchestration (`detector.py`)
- **Domain Layer**: Core logic (video processing, analysis, formatting)
- **Infrastructure Layer**: Agent definitions, configuration files

---

## C4 Model Diagrams

The C4 model provides hierarchical views of the system architecture.

### Level 1: System Context

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                        User / Grader                         │
│                                                              │
│              (Runs detection on video files)                 │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ CLI commands
                         │ (--video, --batch, --provider)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│            Deepfake Detection System                            │
│                                                                 │
│  Analyzes videos for deepfake artifacts using local             │
│  reasoning agent or optional LLM providers                      │
│                                                                 │
│  Input: MP4 videos                                              │
│  Output: Classification, confidence, detailed reasoning         │
│                                                                 │
└───────┬──────────────────────────────┬──────────────────────────┘
        │                              │
        │ (Optional)                   │
        │ API calls                    │ File I/O
        ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│                  │          │                  │
│  External LLM    │          │  File System     │
│  Providers       │          │                  │
│                  │          │  - Videos        │
│  - Anthropic     │          │  - Configs       │
│  - OpenAI        │          │  - Results       │
│                  │          │                  │
└──────────────────┘          └──────────────────┘
```

**Key External Entities**:
- **User/Grader**: Executes system via CLI, reviews analysis results
- **External LLM Providers** (Optional): Anthropic Claude, OpenAI GPT-4V
- **File System**: Video inputs, configuration files, result outputs

---

### Level 2: Container Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Deepfake Detection System                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  CLI Application (detect.py)                   │  │
│  │  Python script                                                 │  │
│  │  - Parse command-line arguments                                │  │
│  │  - Validate inputs                                             │  │
│  │  - Display results                                             │  │
│  └────────────────────┬───────────────────────────────────────────┘  │
│                       │                                              │
│                       │ Calls                                        │
│                       ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │             Detector Orchestrator (detector.py)               │  │
│  │  Python module                                                 │  │
│  │  - Coordinate detection pipeline                               │  │
│  │  - Manage analysis flow                                        │  │
│  │  - Handle errors                                               │  │
│  └──┬────────────────┬───────────────────┬────────────────────┬──┘  │
│     │                │                   │                    │     │
│     │ Uses           │ Uses              │ Uses               │ Uses│
│     ▼                ▼                   ▼                    ▼     │
│  ┌────────┐  ┌──────────────┐  ┌───────────────┐  ┌─────────────┐ │
│  │ Video  │  │   Analyzer   │  │    Output     │  │   Local     │ │
│  │Process │  │ (Multi-prov) │  │   Formatter   │  │   Agent     │ │
│  │   or   │  │              │  │               │  │  (Default)  │ │
│  │        │  │ - Local      │  │ - Console     │  │             │ │
│  │ - Meta │  │ - Anthropic  │  │ - JSON        │  │ - Rules     │ │
│  │   data │  │ - OpenAI     │  │ - Text        │  │ - OpenCV    │ │
│  │ - Frame│  │ - Mock       │  │               │  │ - YAML      │ │
│  │  extr. │  │              │  │               │  │   config    │ │
│  └────────┘  └──────────────┘  └───────────────┘  └─────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Container Responsibilities**:

1. **CLI Application**: User interface, argument parsing, result display
2. **Detector Orchestrator**: Pipeline coordination, error handling
3. **Video Processor**: FFmpeg integration, metadata extraction, frame sampling
4. **Analyzer**: Multi-provider analysis (local agent, LLMs)
5. **Output Formatter**: Result formatting (console, JSON, text)
6. **Local Agent**: Self-contained reasoning logic (default provider)

---

### Level 3: Component Diagram (Detector Orchestrator)

```
┌─────────────────────────────────────────────────────────────────┐
│              Detector Orchestrator (detector.py)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           DeepfakeDetector Class                          │  │
│  │                                                            │  │
│  │  + analyze_video(path, provider, ...)                     │  │
│  │  + batch_analyze(paths, ...)                              │  │
│  │  - _process_single_video()                                │  │
│  │  - _handle_error()                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          │ Delegates to                        │
│                          ▼                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Pipeline Components                        │   │
│  │                                                          │   │
│  │  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐ │   │
│  │  │VideoProcessor │  │   Analyzer   │  │   Formatter  │ │   │
│  │  │               │  │              │  │              │ │   │
│  │  │ extract_meta()│  │ analyze()    │  │ format()     │ │   │
│  │  │ sample_frames│  │              │  │              │ │   │
│  │  └───────────────┘  └──────────────┘  └──────────────┘ │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Component Interactions**:
1. `DeepfakeDetector` receives analysis request
2. Delegates video processing to `VideoProcessor`
3. Passes frames to `Analyzer` (strategy pattern selects provider)
4. Receives analysis results
5. Formats output via `OutputFormatter`
6. Returns formatted results

---

### Level 4: Code Diagram (Local Agent)

```
┌──────────────────────────────────────────────────────────────────┐
│            Local Reasoning Agent (local_agent.py)                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          LocalDeepfakeAgent Class                           │ │
│  │                                                              │ │
│  │  - agent_config: Dict (from YAML)                           │ │
│  │  - detection_rules: Dict (from YAML)                        │ │
│  │                                                              │ │
│  │  + analyze(frames, metadata) → Dict                         │ │
│  │  - _analyze_visual_artifacts(frame) → Score                 │ │
│  │  - _analyze_temporal_consistency(frames) → Score            │ │
│  │  - _synthesize_verdict(visual, temporal) → Classification   │ │
│  │  - _generate_reasoning(scores, evidence) → String           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                          │                                       │
│                          │ Uses                                  │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Detection Heuristics (OpenCV)                    │ │
│  │                                                              │ │
│  │  - Laplacian variance (facial smoothing detection)          │ │
│  │  - Sobel gradients (lighting inconsistency)                 │ │
│  │  - Canny edges (boundary artifacts)                         │ │
│  │  - Frame differencing (temporal consistency)                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                          │                                       │
│                          │ Configured by                         │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Agent Configuration Files                      │ │
│  │                                                              │ │
│  │  - agent_definition.yaml: Metadata, thresholds, weights     │ │
│  │  - detection_rules.yaml: Heuristic rules, scoring logic     │ │
│  │  - system_prompt.md: Reasoning framework documentation      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Key Methods**:
- `_analyze_visual_artifacts()`: Applies OpenCV heuristics (Laplacian, Sobel, Canny)
- `_analyze_temporal_consistency()`: Computes frame-to-frame differences
- `_synthesize_verdict()`: Combines scores using weighted formula
- `_generate_reasoning()`: Produces natural language explanation

---

## Component Interactions

### Sequence Diagram: Video Analysis Flow

```
User          CLI          Detector       VideoProc      Analyzer      LocalAgent     Formatter
 │             │              │              │              │              │              │
 │──analyze──>│              │              │              │              │              │
 │             │──analyze_──>│              │              │              │              │
 │             │   video     │              │              │              │              │
 │             │              │──extract───>│              │              │              │
 │             │              │   metadata  │              │              │              │
 │             │              │<──metadata──│              │              │              │
 │             │              │              │              │              │              │
 │             │              │──sample────>│              │              │              │
 │             │              │   frames    │              │              │              │
 │             │              │<──frames────│              │              │              │
 │             │              │              │              │              │              │
 │             │              │─────analyze────────────────>│              │              │
 │             │              │                             │──analyze───>│              │
 │             │              │                             │   (local)   │              │
 │             │              │                             │              │──visual────>│
 │             │              │                             │              │──temporal──>│
 │             │              │                             │              │──synthesis─>│
 │             │              │                             │<──results────│              │
 │             │              │<─────results────────────────│              │              │
 │             │              │              │              │              │              │
 │             │              │─────────format──────────────────────────────────────────>│
 │             │              │<────────formatted_output────────────────────────────────│
 │             │<──results───│              │              │              │              │
 │<──display───│              │              │              │              │              │
 │   results   │              │              │              │              │              │
```

**Flow Steps**:
1. User invokes CLI with video path
2. CLI calls Detector.analyze_video()
3. Detector extracts metadata via VideoProcessor
4. Detector samples frames via VideoProcessor
5. Detector calls Analyzer with frames
6. Analyzer delegates to LocalAgent (strategy pattern)
7. LocalAgent performs visual + temporal + synthesis
8. Results flow back through layers
9. Formatter creates output
10. CLI displays to user

---

## Data Flow

### Data Transformations

```
┌──────────────┐
│  MP4 Video   │
│  (Input)     │
└──────┬───────┘
       │
       │ VideoProcessor.extract_metadata()
       ▼
┌──────────────────────┐
│  Video Metadata      │
│  {                   │
│    duration: 5.2s    │
│    resolution: 1920x │
│    fps: 30           │
│    codec: h264       │
│  }                   │
└──────┬───────────────┘
       │
       │ VideoProcessor.sample_frames()
       ▼
┌──────────────────────┐
│  Frame Array         │
│  [                   │
│    frame_0 (numpy),  │
│    frame_1 (numpy),  │
│    ...               │
│    frame_9 (numpy)   │
│  ]                   │
└──────┬───────────────┘
       │
       │ LocalAgent.analyze()
       ▼
┌──────────────────────┐
│  Heuristic Scores    │
│  {                   │
│    visual: 0.35,     │
│    temporal: 0.90,   │
│    combined: 0.52    │
│  }                   │
└──────┬───────────────┘
       │
       │ LocalAgent._synthesize_verdict()
       ▼
┌──────────────────────────────┐
│  Analysis Results            │
│  {                           │
│    classification: UNCERTAIN │
│    confidence: 50%,          │
│    reasoning: "...",         │
│    evidence: [...]           │
│  }                           │
└──────┬───────────────────────┘
       │
       │ OutputFormatter.format_*()
       ▼
┌──────────────────────┐      ┌──────────────────────┐
│  Console Output      │      │  JSON/Text Files     │
│  (Human-readable)    │      │  (Structured data)   │
└──────────────────────┘      └──────────────────────┘
```

---

## Deployment Architecture

### Operational Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User's Local Machine                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Python Environment (3.9+)                              │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  deepfake-detection/                              │  │    │
│  │  │  - src/                                           │  │    │
│  │  │  - agents/deepfake_detector_v1.0/                 │  │    │
│  │  │  - detect.py                                      │  │    │
│  │  │  - pyproject.toml                                 │  │    │
│  │  │  - .env (optional)                                │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  Dependencies:                                          │    │
│  │  - opencv-python (computer vision)                      │    │
│  │  - PyYAML (configuration)                               │    │
│  │  - anthropic (optional, LLM mode)                       │    │
│  │  - python-dotenv (env vars)                             │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  System Dependencies                                    │    │
│  │  - FFmpeg (video processing)                            │    │
│  │  - Python 3.9+ runtime                                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  File System                                            │    │
│  │  - data/videos/  (input videos)                         │    │
│  │  - results/      (analysis outputs)                     │    │
│  │  - agents/       (agent configs)                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ (Optional)
                               │ HTTPS API calls
                               ▼
                   ┌──────────────────────────┐
                   │  External Services       │
                   │  - Anthropic API         │
                   │  - OpenAI API            │
                   └──────────────────────────┘
```

**Deployment Notes**:
- **Self-Contained**: Runs entirely on user's machine (default local agent mode)
- **No Server Required**: CLI application, not web service
- **Optional Cloud**: External LLM APIs only needed if using `--provider anthropic/openai`
- **Zero Configuration**: Works out-of-box with local agent (no API keys needed)

---

## Parallel Processing Architecture

### Overview

The system supports **parallel processing** for performance optimization using both multiprocessing and multithreading:
- **Multiprocessing** for CPU-bound frame extraction
- **Multithreading** for I/O-bound LLM API calls

This provides 2-4x speedup for frame-heavy workloads while maintaining thread safety and resource cleanup.

### Components

#### ParallelFrameProcessor

**Purpose**: Extract video frames in parallel using process pool.

**Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│              ParallelFrameProcessor                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Main Process                                           │ │
│  │  - Validates video path                                 │ │
│  │  - Determines frame indices to extract                  │ │
│  │  - Creates ProcessPoolExecutor                          │ │
│  └──────────────┬──────────────────────────────────────────┘ │
│                 │                                            │
│                 │ Distributes work                           │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Worker Process Pool                                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Worker 1: Extract frame[0]                           │   │
│  │  Worker 2: Extract frame[10]                          │   │
│  │  Worker 3: Extract frame[20]                          │   │
│  │  Worker 4: Extract frame[30]                          │   │
│  │  ...                                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                 │                                            │
│                 │ Returns frames                             │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Result Aggregation                                   │   │
│  │  - Collects frames from workers                       │   │
│  │  - Sorts by frame index                               │   │
│  │  - Tracks failures and timing                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Key Features**:
- **Process Pool**: Uses `ProcessPoolExecutor` with configurable workers (default: CPU count)
- **Static Method**: `_extract_single_frame()` is static for pickling (multiprocessing requirement)
- **Timeout Handling**: Each frame extraction has configurable timeout (default: 30s)
- **Failure Tracking**: Failed frames logged but don't block pipeline
- **Color Space**: Supports RGB/BGR output

**Performance**:
- Sequential: ~0.5s per frame (10 frames = 5s)
- Parallel (4 cores): ~0.15s per frame (10 frames = 1.5s)
- **Speedup**: ~3.3x on quad-core CPU

#### ParallelLLMAnalyzer

**Purpose**: Perform concurrent LLM API calls with rate limiting.

**Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│              ParallelLLMAnalyzer                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Main Thread                                            │ │
│  │  - Receives frames and analysis function                │ │
│  │  - Creates ThreadPoolExecutor                           │ │
│  └──────────────┬──────────────────────────────────────────┘ │
│                 │                                            │
│                 │ Distributes API calls                      │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Thread Pool (with Semaphore for Concurrency Control) │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Thread 1: ─┐                                         │   │
│  │  Thread 2: ─┼─ Semaphore (max 5 concurrent)          │   │
│  │  Thread 3: ─┤                                         │   │
│  │  Thread 4: ─┤                                         │   │
│  │  Thread 5: ─┘                                         │   │
│  │  Thread 6: waiting...                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                 │                                            │
│                 │ Each thread:                               │
│                 │ - Acquires semaphore                       │
│                 │ - Applies rate limit delay                 │
│                 │ - Calls analysis function                  │
│                 │ - Retries on failure (exponential backoff) │
│                 │ - Releases semaphore                       │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Result Collection                                    │   │
│  │  - Thread-safe result aggregation                     │   │
│  │  - Error handling and logging                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Key Features**:
- **Semaphore**: Limits concurrent API calls (default: 5) to prevent rate limit errors
- **Rate Limiting**: Configurable delay between requests (default: 0.5s)
- **Retry Logic**: Exponential backoff on failures (default: 2 retries)
- **Thread Safety**: Uses locks for shared state access
- **Graceful Degradation**: Failed analyses logged, don't block others

**Performance**:
- Sequential: 10 frames × 2s/frame = 20s
- Parallel (5 concurrent): 10 frames / 5 × 2s = 4s
- **Speedup**: ~5x (limited by concurrency cap)

### When to Use Multiprocessing vs. Multithreading

| Operation Type | Method | Reason |
|---------------|--------|--------|
| **Frame Extraction** | Multiprocessing | CPU-bound (video decoding, color conversion) |
| **LLM API Calls** | Multithreading | I/O-bound (network waiting, GIL doesn't matter) |
| **Heuristic Computation** | Multiprocessing | CPU-bound (OpenCV operations) |
| **File I/O** | Multithreading | I/O-bound (disk reading/writing) |

### Thread Safety and Race Condition Prevention

**Mechanisms**:
1. **Semaphores**: Limit concurrent resource access
2. **Locks**: Protect shared state modifications
3. **Immutable Data**: Pass immutable numpy arrays, not shared state
4. **Process Isolation**: Each worker process has independent memory

**Example - Thread-Safe Counter**:
```python
class ThreadSafeAnalyzer:
    def __init__(self):
        self._lock = threading.Lock()
        self._counter = 0

    def increment(self):
        with self._lock:  # Prevents race conditions
            self._counter += 1
```

### Resource Cleanup

**Automatic Cleanup**:
- **Context Managers**: `with ProcessPoolExecutor()` ensures process termination
- **Finally Blocks**: VideoCapture released even on exceptions
- **Signal Handlers**: Graceful shutdown on SIGINT (Ctrl+C)

**ResourceManager** (utility class):
```python
with ResourceManager() as manager:
    # All pools/executors tracked
    # Cleaned up automatically on exit or exception
```

### Benchmarking

**Performance Testing**:
```bash
# Benchmark parallel vs sequential
from src.parallel_processor import ParallelFrameProcessor

processor = ParallelFrameProcessor(max_workers=4)
benchmark = processor.benchmark_speedup(
    video_path="test.mp4",
    frame_indices=list(range(0, 100, 10))
)

print(f"Sequential: {benchmark['sequential_time']:.2f}s")
print(f"Parallel: {benchmark['parallel_time']:.2f}s")
print(f"Speedup: {benchmark['speedup']:.2f}x")
```

**Expected Results** (10-frame extraction):
- Sequential: ~5.0s
- Parallel (4 cores): ~1.5s
- **Speedup**: ~3.3x

**Optimal Workers Detection**:
```python
from src.parallel_processor import detect_optimal_workers

optimal_workers = detect_optimal_workers(
    video_path="test.mp4",
    test_frame_count=10
)
# Returns: 4 (or cpu_count, whichever performs best)
```

### CLI Integration

**Usage**:
```bash
# Enable parallel frame extraction
python detect.py --video test.mp4 --parallel

# Specify custom worker count
python detect.py --video test.mp4 --parallel --workers 8

# Automatic optimal detection
python detect.py --video test.mp4 --parallel --workers auto
```

**Performance Recommendations**:
- **Small videos (<10 frames)**: Sequential may be faster (overhead > benefit)
- **Medium videos (10-30 frames)**: Parallel with default workers
- **Large videos (>30 frames)**: Parallel with 2x CPU count workers
- **Batch processing**: Parallel essential for reasonable runtime

### Testing

**Test Coverage**:
- ✅ Multiprocessing correctness (frames match sequential)
- ✅ Thread safety (no race conditions under concurrent load)
- ✅ Deadlock prevention (all tests complete without hanging)
- ✅ Resource cleanup (no zombie processes, proper context manager exit)
- ✅ Error handling (failures don't crash, logged gracefully)
- ✅ Performance benchmarks (speedup verification)

See `tests/test_parallel_processor.py` for comprehensive test suite.

---

## Architecture Decision Records (ADRs)

### ADR-001: Layered Architecture with Strategy Pattern

**Date**: December 20, 2025
**Status**: Accepted

**Context**:
Need modular architecture supporting multiple analysis providers (local agent, Claude, GPT-4V, mock).

**Decision**:
Implement layered architecture with Strategy Pattern for analysis providers.

**Consequences**:
- ✅ Easy to add new providers
- ✅ Clear separation of concerns
- ✅ Testable components
- ⚠️ Slight overhead from abstraction layers

---

### ADR-002: Local Agent as Default Provider

**Date**: December 29, 2025
**Status**: Accepted

**Context**:
LLM-based analysis has reproducibility issues, costs money, requires API keys. Academic evaluation needs deterministic results.

**Decision**:
Make local reasoning agent the default provider. Keep LLM providers as optional.

**Consequences**:
- ✅ Perfect reproducibility (deterministic)
- ✅ Zero cost (no API calls)
- ✅ Zero setup (no API keys needed)
- ✅ Ideal for academic grading
- ⚠️ Lower accuracy than state-of-the-art deep learning
- ⚠️ Fixed heuristics may not generalize

**Trade-off**: Prioritize reproducibility and transparency over raw accuracy.

---

### ADR-003: OpenCV for Visual Analysis

**Date**: December 27, 2025
**Status**: Accepted

**Context**:
Need computer vision techniques for local agent. Options: OpenCV, scikit-image, custom implementations.

**Decision**:
Use OpenCV for all computer vision operations (Laplacian, Sobel, Canny, frame differencing).

**Consequences**:
- ✅ Well-tested, battle-hardened library
- ✅ Fast, optimized implementations
- ✅ Comprehensive documentation
- ✅ Widely used in academia/industry
- ⚠️ Large dependency (~50MB)

---

### ADR-004: YAML for Agent Configuration

**Date**: December 28, 2025
**Status**: Accepted

**Context**:
Need human-readable, version-controllable configuration for agent rules and thresholds.

**Decision**:
Use YAML files for agent configuration (`agent_definition.yaml`, `detection_rules.yaml`).

**Consequences**:
- ✅ Human-readable, easy to edit
- ✅ Version-controllable
- ✅ Supports comments and structure
- ✅ Python support via PyYAML
- ⚠️ No schema validation (could add JSON Schema)

---

### ADR-005: Multi-Stage Analysis Pipeline

**Date**: December 24, 2025
**Status**: Accepted

**Context**:
Deepfake detection requires both visual artifact detection and temporal consistency analysis.

**Decision**:
Implement three-stage pipeline: (1) Visual Analysis, (2) Temporal Analysis, (3) Synthesis.

**Consequences**:
- ✅ Clear separation of concerns
- ✅ Easier to debug and improve
- ✅ Matches LLM prompt structure
- ✅ Modular scoring system
- ⚠️ More complex than single-stage

**Rationale**: Multi-stage mirrors how humans analyze videos (look at frames, then motion, then combine).

---

### ADR-006: 60/40 Visual-Temporal Weighting

**Date**: December 28, 2025
**Status**: Accepted

**Context**:
Need to combine visual and temporal scores. What weights to use?

**Decision**:
Use 60% visual, 40% temporal weighting.

$$\text{Combined} = 0.6 \times \text{Visual} + 0.4 \times \text{Temporal}$$

**Consequences**:
- ✅ Visual artifacts more reliable indicator
- ✅ Temporal consistency still significant
- ✅ Balanced approach
- ⚠️ Weights are empirically chosen, not optimized

**Rationale**: Visual artifacts (smoothing, lighting) are primary deepfake indicators. Temporal consistency is secondary but important.

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Runtime** | Python 3.9+ | Core language |
| **Computer Vision** | OpenCV 4.10+ | Visual heuristics |
| **Configuration** | PyYAML 6.0+ | YAML parsing |
| **CLI** | argparse | Command-line interface |
| **Testing** | pytest 8.0+ | Unit testing |
| **Video Processing** | FFmpeg | Metadata extraction, frame sampling |
| **LLM Integration** | Anthropic SDK, OpenAI SDK | Optional external providers |
| **Environment** | python-dotenv | Environment variable management |

---

## Security Considerations

### API Key Management

```
┌────────────────────────────────┐
│  .env (not in version control) │
│  ANTHROPIC_API_KEY=sk-ant-...  │
│  OPENAI_API_KEY=sk-...         │
└────────────────────────────────┘
                │
                │ Loaded by python-dotenv
                ▼
┌────────────────────────────────┐
│  Environment Variables          │
│  (Runtime memory)               │
└────────────────────────────────┘
                │
                │ Accessed by
                ▼
┌────────────────────────────────┐
│  LLM Provider Classes           │
│  (Only if using LLM mode)       │
└────────────────────────────────┘
```

**Security Measures**:
- ✅ API keys in `.env` (git-ignored)
- ✅ Environment variables, not hardcoded
- ✅ `.env.example` template provided
- ✅ Local agent mode requires zero secrets

---

## Performance Characteristics

| Metric | Local Agent | LLM Provider (Claude) |
|--------|-------------|----------------------|
| **Execution Time** (10 frames) | ~2-3 seconds | ~15-30 seconds |
| **Memory Usage** | ~200-300 MB | ~300-400 MB |
| **CPU Usage** | High (OpenCV operations) | Low (waiting for API) |
| **Network** | None (offline) | HTTPS API calls |
| **Cost** | $0.00 | $0.10-0.40 per video |
| **Reproducibility** | 100% (deterministic) | Variable (LLM stochastic) |

---

## Extensibility Points

### Adding New Analysis Providers

1. Create provider class implementing `analyze()` method
2. Add to `llm_analyzer.py` provider factory
3. Update CLI argument parser
4. Add tests in `test_llm_analyzer.py`

### Adding New Heuristics

1. Update `detection_rules.yaml` with new rule
2. Implement heuristic in `local_agent.py`
3. Update scoring logic in `_analyze_visual_artifacts()` or `_analyze_temporal_consistency()`
4. Document in `agents/deepfake_detector_v1.0/README.md`

### Adding New Output Formats

1. Implement formatter method in `output_formatter.py`
2. Add CLI option for new format
3. Update tests in `test_output_formatter.py`

---

## References

- **C4 Model**: [https://c4model.com/](https://c4model.com/)
- **Layered Architecture**: Fowler, M. "Patterns of Enterprise Application Architecture"
- **Strategy Pattern**: Gamma et al. "Design Patterns: Elements of Reusable Object-Oriented Software"
- **OpenCV Documentation**: [https://docs.opencv.org/](https://docs.opencv.org/)

---

**Document Version**: 1.0
**Last Updated**: December 29, 2025
**Status**: Complete
