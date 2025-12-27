# Deepfake Video Directory

This directory contains deepfake (synthetic) videos generated for testing the LLM-based detection system.

## Contents

### Primary Test Video

**Filename**: `deepfake_inframe_v1.mp4`
**Status**: _To be added_
**Generation Method**: Google Flow (Inframe option)

**Purpose**: Test case for the deepfake detection system. This video is generated from a single still image and should exhibit characteristics typical of deepfake content.

### Source Materials

**Filename**: `source_image.jpg` (or similar)
**Status**: _To be added_
**Description**: Original still image used to generate the deepfake video

### Sample Frames

Optional: Extracted frames for documentation purposes

---

## Video Specifications

_To be filled after generation_

### Expected Metadata

```
Format: MP4
Codec: H.264 or H.265
Resolution: 720p or higher (recommended 1080p)
Duration: 3-10 seconds
Frame Rate: 24-60 fps
File Size: <50 MB (preferably <20 MB)
```

### Generation Details

- **Tool**: Google Flow (Inframe option)
- **Generation Date**: _[To be filled]_
- **Source Image**: _[Description]_
- **Settings**: _[Configuration details]_

Full generation documentation: See `docs/deepfake_generation.md`

---

## Ethical Statement

All videos in this directory are:
- Generated for **academic research purposes only**
- Part of Assignment 09 - Deepfake Detection
- **Not intended for malicious use or public distribution**
- Clearly labeled as synthetic content
- Used to develop detection methodologies

---

## Usage

These videos will be used by the detection system as follows:

```bash
# Analyze deepfake video
python detect_deepfake.py --video data/videos/fake/deepfake_inframe_v1.mp4

# Expected output: Classification as "FAKE" with detailed reasoning
```

---

## Characteristics to Test

The deepfake video should exhibit some of the following characteristics that the LLM-based detector should identify:

### Visual Artifacts
- Facial smoothing or unnatural texture
- Lighting inconsistencies (face vs. background)
- Warping near face boundaries
- Resolution mismatches

### Temporal Artifacts
- Unnatural motion or jitter
- Inconsistent blinking patterns
- Frame-to-frame discontinuities
- Micro-artifacts in transitions

### Semantic Anomalies
- Lip sync issues (if applicable)
- Unnatural expressions or movements
- Physical impossibilities

---

## File Status

- [ ] `deepfake_inframe_v1.mp4` - Primary deepfake video
- [ ] `source_image.jpg` - Source still image
- [ ] Additional sample frames (optional)

**Last Updated**: 2025-12-27
**Status**: Awaiting video generation
