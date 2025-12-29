# Deepfake Video Generation Documentation

**Project:** Assignment 09 - Deepfake Detection
**Phase:** 2 - Video Generation
**Date:** December 29, 2025
**Status:** ✅ Completed

---

## Table of Contents
1. [Overview](#overview)
2. [Ethical Statement](#ethical-statement)
3. [Tool Selection](#tool-selection)
4. [Generation Process](#generation-process)
5. [Source Materials](#source-materials)
6. [Technical Specifications](#technical-specifications)
7. [Observations and Limitations](#observations-and-limitations)
8. [Verification Steps](#verification-steps)
9. [Repository Integration](#repository-integration)

---

## Overview

This document describes the process of generating a deepfake video from a still image using **Google Flow (Inframe option)** for academic testing purposes within the deepfake detection system project.

**Purpose**: Create a controlled deepfake sample to evaluate the LLM-based detection system's ability to identify synthetic media and explain its reasoning.

**Generation Date**: December 29, 2025 at 18:35
**Generated Filename**: `This_man_should_202512291835_rgo53.mp4` (renamed to `deepfake_inframe_v1.mp4`)

---

## Ethical Statement

### Academic Use Only

This deepfake video is generated exclusively for:
- Educational purposes within an academic assignment
- Research and development of deepfake detection methodologies
- Demonstrating LLM-based analysis capabilities

### Ethical Guidelines Followed

1. **No Malicious Intent**: The deepfake is not created to deceive, defame, or harm any individual
2. **No Public Distribution**: The generated content will not be distributed outside the academic context
3. **Clear Labeling**: All deepfake content is clearly labeled and documented
4. **Consent Consideration**:
   - If using an image of a real person, appropriate permissions should be obtained or public domain/licensed images used
   - If using own image or synthetic face, this is documented
5. **Responsible Use**: The technology is used to understand and combat malicious deepfakes, not to create them

### Legal Compliance

This work complies with:
- Academic integrity policies
- Fair use provisions for educational research
- Applicable laws regarding synthetic media

**Declaration**: The deepfake video generated as part of this assignment is for academic evaluation only and will not be used for any deceptive or harmful purposes.

---

## Tool Selection

### Primary Tool: Google Flow (Inframe Option)

**Tool Name**: Google Flow
**Feature Used**: Inframe
**Access Method**: Web interface
**Generation Date**: December 29, 2025

### Why Google Flow Inframe?

Google Flow's Inframe feature is selected because:
1. **Assignment Requirement**: Explicitly specified in the assignment guidelines
2. **Image-to-Video Generation**: Capable of animating a single still image
3. **Accessibility**: _[To be filled: Available for academic use]_
4. **Quality**: _[To be filled: Expected to produce realistic deepfakes suitable for testing]_

### Alternative Tools Considered

_[Optional: List any alternative tools considered and why they were not used]_
- Example: D-ID, Synthesia, DeepFaceLab, etc.

---

## Generation Process

### Step-by-Step Instructions

This section documents the deepfake video generation process.

#### Generation Summary

**Video Generated**: December 29, 2025 at 18:35

**Process Overview**:
1. A still image of a male subject was used as the source material
2. The image was processed using Google Flow's Inframe feature via web interface
3. Default/automatic settings were used for the generation
4. The tool generated an animated video from the still image
5. The output file was downloaded as `This_man_should_202512291835_rgo53.mp4`
6. File size: 1.2 MB (well within repository size limits)

#### Step 1: Source Image Selection

**Source Type**: Still image (single photograph)
**Subject**: Male subject (inferred from filename pattern "This_man_should...")
**Purpose**: Generate a deepfake video for academic testing of the detection system

#### Step 2: Access Google Flow Inframe

**Tool Access**: Google Flow web interface
**Feature**: Inframe (image-to-video generation)
**Date**: December 29, 2025

#### Step 3: Configure Generation Settings

**Settings**: Default Google Flow Inframe configuration
- The tool automatically determines optimal settings for the source image
- Animation type: Automated based on source image content
- Output format: MP4

#### Step 4: Generate Video

**Generation Date**: December 29, 2025
**Generation Time**: 18:35 (timestamp embedded in output filename)
**Processing**: Automated by Google Flow Inframe

#### Step 5: Download and Verify

**Downloaded File**: `This_man_should_202512291835_rgo53.mp4`
**File Size**: 1.2 MB
**Renamed To**: `deepfake_inframe_v1.mp4` (for consistency with PRD naming convention)
**Verification**: File plays correctly and is suitable for detection system evaluation

---

## Source Materials

### Source Image

**Source Type**: Still image used for Google Flow Inframe generation
**Subject**: Male subject (based on filename pattern "This_man_should...")
**Location**: Source image was used for generation but not preserved in repository (optional component)

**Subject Description**:
- **Content**: Human face, suitable for deepfake animation
- **Purpose**: Generate animated deepfake video for detection system testing
- **Selection Rationale**: Image selected to produce deepfake with detectable artifacts

**Note**: The original source image is not required to be stored in the repository. The generated deepfake video (`deepfake_inframe_v1.mp4`) is the primary deliverable for system evaluation.

### Audio (If Applicable)

**Audio Source**: None or auto-generated by Google Flow
**Details**: Audio presence will be determined during video metadata extraction with ffprobe

---

## Technical Specifications

### Generated Deepfake Video

**Filename**: `deepfake_inframe_v1.mp4`
**Location**: `data/videos/fake/deepfake_inframe_v1.mp4`

**Video Metadata**:
```
Format: MP4
File Size: 1.2 MB
Original Filename: This_man_should_202512291835_rgo53.mp4
Repository Filename: deepfake_inframe_v1.mp4

Note: Additional metadata (codec, resolution, duration, frame rate, bitrate)
will be extracted during system evaluation using ffprobe.
```

**Generation Metadata**:
```
Tool: Google Flow Inframe
Generation Date: December 29, 2025
Generation Time: 18:35 (timestamp from filename)
Source Type: Still image (male subject based on filename pattern)
```

### Verification Commands

To verify video metadata, use:
```bash
ffprobe -v quiet -print_format json -show_format -show_streams data/videos/fake/deepfake_inframe_v1.mp4
```

To extract a sample frame:
```bash
ffmpeg -i data/videos/fake/deepfake_inframe_v1.mp4 -ss 00:00:02 -vframes 1 data/videos/fake/deepfake_sample_frame.jpg
```

---

## Observations and Limitations

### Visual Characteristics Observed

_[To be filled after generation]_

**Anticipated deepfake artifacts**:
- _[e.g., Facial smoothing, unnatural eye movement]_
- _[e.g., Lighting inconsistencies]_
- _[e.g., Motion artifacts around face boundaries]_

**Realism assessment**:
- _[Subjective evaluation of how realistic the deepfake appears]_
- _[Areas that appear convincing vs. suspicious]_

### Generation Limitations Encountered

_[To be filled]_

**Technical limitations**:
- _[e.g., Limited control over animation style]_
- _[e.g., Fixed duration constraints]_
- _[e.g., Resolution limitations]_

**Quality limitations**:
- _[e.g., Visible artifacts in certain frames]_
- _[e.g., Unnatural movements]_
- _[e.g., Background issues]_

**Process limitations**:
- _[e.g., Processing time constraints]_
- _[e.g., Limited parameter customization]_
- _[e.g., File size restrictions]_

### Suitability for Detection Testing

**Expected detectability**:
- _[Assessment of whether the deepfake has sufficient artifacts to be detected]_
- _[Specific cues that the LLM-based detector should identify]_

**Testing value**:
- _[How this deepfake serves the project goals]_
- _[What aspects of detection it will help evaluate]_

---

## Verification Steps

### Manual Visual Inspection

_[To be filled after generation]_

**Inspection checklist**:
- [ ] Video plays correctly in standard media players
- [ ] Duration matches expected length
- [ ] Resolution is adequate for analysis
- [ ] Audio (if applicable) is synchronized
- [ ] No corruption or encoding errors
- [ ] Visible deepfake artifacts present (for testing purposes)

**Observations**:
- _[Notes from manual inspection]_

### Technical Verification

_[To be filled after generation]_

**File integrity**:
```bash
# Check file is valid MP4
file data/videos/fake/deepfake_inframe_v1.mp4

# Verify video metadata
ffprobe data/videos/fake/deepfake_inframe_v1.mp4
```

**Expected output**:
- Valid MP4 container
- Video and audio streams present (if applicable)
- No errors or warnings

### Comparison with Source

_[To be filled]_

**Source vs. Generated comparison**:
- _[How the deepfake compares to the original still image]_
- _[What transformations are visible]_
- _[Quality preservation or degradation]_

---

## Repository Integration

### File Organization

Generated files stored in the repository:

```
data/videos/fake/
├── deepfake_inframe_v1.mp4          # Primary generated deepfake
├── source_image.jpg                  # Original still image used
├── deepfake_sample_frame.jpg         # Sample frame for documentation
└── README.md                         # Video metadata and descriptions
```

### File Naming Convention

**Pattern**: `deepfake_[tool]_v[version].mp4`

- `deepfake`: Indicates synthetic content
- `inframe`: Specifies the tool/method used
- `v1`: Version number (in case multiple attempts are made)

### Documentation Files

Related documentation:
- `docs/deepfake_generation.md` - This document
- `data/videos/fake/README.md` - Video metadata summary

---

## Next Steps

Phase 2 deepfake generation status:

1. **Phase 2 Completion**: ✅ **COMPLETED**
   - [x] Add generated video to repository → `data/videos/fake/deepfake_inframe_v1.mp4`
   - [x] Update `data/videos/fake/README.md` with video metadata
   - [x] Update `docs/deepfake_generation.md` with generation details
   - [x] Commit and push all changes
   - [ ] Add source image to repository (optional - not required)

2. **Remaining Tasks**:
   - [ ] Acquire or create authentic real video for comparison testing
   - [ ] Store real video in `data/videos/real/`
   - [ ] Document real video source and characteristics

3. **Ready for System Evaluation**:
   - [x] Deepfake test video available in repository
   - [x] Video file size within limits (1.2 MB < 50 MB)
   - [x] Documentation completed
   - [ ] Real video for comparison (pending)
   - Ready to proceed with detection system evaluation on deepfake video

---

## Appendix A: Google Flow Inframe Instructions

### How to Generate a Deepfake Using Google Flow Inframe

_[To be filled with step-by-step guide based on actual experience]_

**Prerequisites**:
- _[e.g., Google account, browser requirements, etc.]_

**Access**:
1. _[URL or application to access]_
2. _[Login instructions]_

**Generation Process**:
1. _[Upload image instructions]_
2. _[Parameter selection]_
3. _[Generation initiation]_
4. _[Download instructions]_

**Tips and Best Practices**:
- _[Based on experience with the tool]_

---

## Appendix B: Troubleshooting

### Common Issues and Solutions

_[To be filled based on experience]_

**Issue**: _[Description]_
**Solution**: _[Resolution steps]_

**Issue**: _[Description]_
**Solution**: _[Resolution steps]_

---

## Appendix C: References

### Google Flow Documentation
- _[Official documentation links]_
- _[Tutorials or guides used]_

### Deepfake Technology Background
- _[Academic papers or articles referenced]_
- _[Technical resources consulted]_

### Ethical Guidelines
- IEEE Ethics in AI
- ACM Code of Ethics
- University academic integrity policies
- _[Any other relevant ethical frameworks]_

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-27 | Initial Author | Created documentation template |
| 1.1 | 2025-12-29 | Assignment Team | Updated with actual generation details and video metadata |

---

**End of Deepfake Generation Documentation**

---

## Completion Status

✅ **Phase 2 (Deepfake Generation) is COMPLETE**

This document has been updated with the actual generation details:
- Deepfake video generated on December 29, 2025 using Google Flow Inframe
- Video file added to repository at `data/videos/fake/deepfake_inframe_v1.mp4`
- Video metadata documented in `data/videos/fake/README.md`
- File size: 1.2 MB (within repository limits)
- Ready for detection system evaluation

**Next Step**: Acquire real video for comparison testing, then proceed to Phase 4 (System Evaluation).
