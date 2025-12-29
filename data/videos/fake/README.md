# Deepfake Video Directory

This directory contains deepfake (synthetic) videos generated for testing the LLM-based detection system.

## Contents

### Primary Test Video

**Filename**: `deepfake_inframe_v1.mp4`
**Status**: ✅ **Added** (December 29, 2025)
**Generation Method**: Google Flow (Inframe option)
**File Size**: 1.2 MB
**Original Filename**: `This_man_should_202512291835_rgo53.mp4`

**Purpose**: Test case for the deepfake detection system. This video is generated from a single still image and should exhibit characteristics typical of deepfake content.

### Source Materials

**Filename**: `source_image.jpg` (or similar)
**Status**: _To be added_
**Description**: Original still image used to generate the deepfake video

### Sample Frames

Optional: Extracted frames for documentation purposes

---

## Video Specifications

### Actual Metadata

```
Format: MP4
File Size: 1.2 MB
Generation Date: December 29, 2025 at 18:35
Original Filename: This_man_should_202512291835_rgo53.mp4
```

**Note**: Additional metadata (resolution, duration, frame rate, codec) will be extracted during system evaluation.

### Generation Details

- **Tool**: Google Flow (Inframe option)
- **Generation Date**: December 29, 2025
- **Generation Time**: 18:35 (based on filename timestamp)
- **Source Image**: Still image of a person (male subject based on filename "This_man_should...")
- **Settings**: Default Google Flow Inframe settings

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

- [x] `deepfake_inframe_v1.mp4` - Primary deepfake video ✅ **ADDED**
- [ ] `source_image.jpg` - Source still image (optional)
- [ ] Additional sample frames (optional)

**Last Updated**: 2025-12-29
**Status**: Deepfake video successfully added and ready for evaluation
