# Real (Authentic) Video Directory

This directory contains authentic, non-manipulated videos for testing the LLM-based detection system.

## Contents

### Primary Test Video

**Filename**: `real_video_v1.mp4`
**Status**: ✅ **Added** (December 29, 2025)
**Source**: Vecteezy (stock footage)
**Original Filename**: `vecteezy_focused-man-savoring-pizza-while-brainstorming-on-his-computer_69328397.mov`
**File Size**: 8.5 MB
**Duration**: 21.0 seconds
**Resolution**: 1080x1920 (portrait)
**Frame Rate**: 29.97 fps
**Codec**: H.264

**Purpose**: Control test case for the deepfake detection system. This video should be correctly identified as authentic/real.

---

## Video Requirements

### Technical Specifications

```
Format: MP4
Codec: H.264 or H.265
Resolution: 720p or higher (preferably similar to deepfake video)
Duration: 3-10 seconds
Frame Rate: 24-60 fps
File Size: <50 MB
Content: Human face(s) visible, similar context to deepfake
```

### Quality Requirements

- **Authentic**: No synthetic manipulation or AI generation
- **Clear**: Good lighting, visible facial features
- **Relevant**: Similar content/context to the deepfake video for fair comparison
- **Rights**: Properly sourced with appropriate permissions or licenses

---

## Sourcing Options

### Option 1: Record Original Video
- Use smartphone or camera
- Record yourself or consenting participant
- Ensure good lighting and clear face visibility
- Keep duration short (5-10 seconds)

### Option 2: Use Licensed/Public Domain Video
Sources for free, licensed videos:
- **Pexels Video**: https://www.pexels.com/videos/
- **Pixabay Videos**: https://pixabay.com/videos/
- **Unsplash** (some video content): https://unsplash.com/
- **Creative Commons**: Search for CC0 or CC-BY videos

Search terms: "person talking", "face portrait", "headshot video"

### Option 3: Academic Datasets
- CelebV dataset (if accessible)
- Other research video datasets

**Important**: Ensure proper attribution and licensing compliance.

---

## Ethical Considerations

Real videos should:
- Have appropriate permissions/licenses for use
- Not violate privacy rights
- Be used solely for academic research
- Be clearly documented as authentic content

---

## Expected Detection Behavior

The LLM-based detector should:
- Classify this video as **"REAL"** or with low suspicion
- Note the **absence** of typical deepfake artifacts
- Identify characteristics of authentic video:
  - Natural lighting variations
  - Consistent motion and physics
  - Realistic facial movements and expressions
  - No warping or smoothing artifacts

---

## Documentation

For each real video added:
1. Document source and license
2. Note technical specifications
3. Describe content (subject, setting, actions)
4. Explain why it was chosen as a control sample

---

## File Status

- [x] `real_video_v1.mp4` - Primary authentic video ✅ **ADDED**
- [ ] Additional real videos (optional)

**Last Updated**: 2025-12-29
**Status**: Real video successfully added and ready for evaluation
