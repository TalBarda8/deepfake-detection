# Phase 2 Completion Guide
## Deepfake Video Generation - Action Items

**Status**: Phase 2 structure prepared, awaiting video generation
**Created**: 2025-12-27

---

## Current Status

### ✅ Completed by Claude

1. **Directory Structure Created**:
   ```
   data/videos/fake/     # For deepfake videos
   data/videos/real/     # For authentic videos
   ```

2. **Documentation Templates Created**:
   - `docs/deepfake_generation.md` - Comprehensive documentation template
   - `data/videos/fake/README.md` - Deepfake video metadata
   - `data/videos/real/README.md` - Real video metadata
   - `docs/PHASE2_COMPLETION_GUIDE.md` - This file

3. **Repository Structure**: Aligned with PRD expectations

---

## ⏳ Action Required: Video Generation

**Important**: I (Claude) cannot directly access external tools like Google Flow or generate actual video files. You need to complete the following steps manually.

---

## Step-by-Step Instructions

### Step 1: Generate Deepfake Video Using Google Flow

#### Access Google Flow Inframe

1. **Navigate to Google Flow**:
   - Search for "Google Flow Inframe" or the specific URL for the tool
   - Alternative: If Google Flow is not accessible, use similar tools:
     - D-ID (https://www.d-id.com/) - generates talking videos from photos
     - HeyGen (https://www.heygen.com/) - AI video generation
     - Runway ML (https://runwayml.com/) - various AI video tools
     - Note: If using alternative, update documentation accordingly

2. **Prepare Source Image**:
   - Select or create a still image of a human face
   - Recommended: Use your own photo, public domain image, or properly licensed image
   - Requirements:
     - Clear, frontal or near-frontal face view
     - Good lighting
     - Neutral or simple background
     - High resolution (1080p or higher recommended)
     - Format: JPEG or PNG

#### Generate the Deepfake

3. **Upload Image to Google Flow**:
   - Follow the tool's upload interface
   - Select the Inframe option (or equivalent video generation feature)

4. **Configure Settings**:
   - Duration: 5-10 seconds recommended
   - Animation type: Natural movement, talking, or expression changes
   - Quality: Highest available (1080p if possible)
   - Frame rate: 30 fps recommended
   - Audio: Optional (can be muted or include generated speech)

5. **Generate and Download**:
   - Initiate generation process
   - Wait for processing (may take several minutes)
   - Download the generated MP4 file
   - **Save as**: `deepfake_inframe_v1.mp4`

#### Alternative if Google Flow is Unavailable

If you cannot access Google Flow:

**Option A**: Use D-ID or similar tool
- Upload photo
- Generate short talking video
- Download and use as test deepfake
- Update documentation to reflect tool used

**Option B**: Use a sample deepfake from research datasets
- Search for "deepfake dataset samples"
- Ensure license allows academic use
- Document source clearly

**Option C**: Use any AI video generation tool
- The key is to have a synthetic video to test against
- Tool selection is flexible for academic purposes
- Document the actual tool used

---

### Step 2: Acquire Real (Authentic) Video

You also need an authentic, non-deepfake video for comparison testing.

#### Option A: Record Your Own Video (Recommended)

1. **Use smartphone or webcam**
2. **Record yourself**:
   - Duration: 5-10 seconds
   - Frontal face view
   - Good lighting
   - Simple background
   - Natural movement or talking
3. **Save as MP4**
4. **Rename**: `real_video_v1.mp4`

#### Option B: Download Free Licensed Video

1. **Visit free video sites**:
   - Pexels: https://www.pexels.com/videos/
   - Pixabay: https://pixabay.com/videos/
   - Search: "person talking", "face closeup", "portrait video"

2. **Download short clip** (5-10 seconds)
3. **Trim if needed** using:
   ```bash
   ffmpeg -i input.mp4 -ss 00:00:00 -t 00:00:05 -c copy real_video_v1.mp4
   ```

4. **Ensure license** allows academic use
5. **Document source** in README

---

### Step 3: Add Videos to Repository

Once you have both videos:

1. **Copy files to repository**:
   ```bash
   # Copy deepfake video
   cp /path/to/generated/deepfake_inframe_v1.mp4 data/videos/fake/

   # Copy source image (used to generate deepfake)
   cp /path/to/source_image.jpg data/videos/fake/

   # Copy real video
   cp /path/to/real_video_v1.mp4 data/videos/real/
   ```

2. **Verify files**:
   ```bash
   ls -lh data/videos/fake/
   ls -lh data/videos/real/
   ```

3. **Check file sizes** (should be <50 MB each, preferably <20 MB)

4. **Test playback**:
   - Open each video in a media player
   - Verify they play correctly
   - Note any visible artifacts (expected in deepfake)

---

### Step 4: Complete Documentation

#### Update `docs/deepfake_generation.md`

Open the file and fill in all sections marked `_[To be filled]_`:

**Essential sections**:
1. **Generation Date and Author**
2. **Source Image Details**:
   - Where you got it
   - Why you chose it
   - Technical specs (resolution, format)
3. **Tool Access Method**:
   - Exact URL or application used
   - Steps followed
4. **Generation Settings**:
   - Duration, quality, animation type
   - Any parameters you configured
5. **Technical Specifications**:
   - Run `ffprobe` to get metadata:
     ```bash
     ffprobe data/videos/fake/deepfake_inframe_v1.mp4
     ```
   - Document: codec, resolution, duration, framerate, file size
6. **Observations**:
   - What artifacts do you notice?
   - How realistic does it look?
   - What might give it away as a deepfake?

#### Update `data/videos/fake/README.md`

1. Change status from "To be added" to "Added"
2. Fill in actual video specifications
3. Add generation date
4. Check off file status checkboxes

#### Update `data/videos/real/README.md`

1. Document source of real video
2. Add technical specifications
3. Note license/permissions
4. Check off file status checkboxes

---

### Step 5: Commit and Push to GitHub

Once all videos and documentation are ready:

```bash
# Check what files you're adding
git status

# Add all new files
git add data/videos/fake/deepfake_inframe_v1.mp4
git add data/videos/fake/source_image.jpg
git add data/videos/real/real_video_v1.mp4
git add docs/deepfake_generation.md
git add data/videos/fake/README.md
git add data/videos/real/README.md

# Commit with meaningful message
git commit -m "Complete Phase 2: Add deepfake and real videos with documentation

- Add deepfake video generated using Google Flow (Inframe)
- Add source image used for deepfake generation
- Add authentic real video for comparison testing
- Complete deepfake generation documentation
- Document video metadata and specifications
- Update README files with video details

Phase 2 complete. Ready for Phase 3: Detection system development."

# Push to GitHub
git push origin main
```

---

## Verification Checklist

Before committing, verify:

### Files Present
- [ ] `data/videos/fake/deepfake_inframe_v1.mp4` exists
- [ ] `data/videos/fake/source_image.jpg` exists
- [ ] `data/videos/real/real_video_v1.mp4` exists

### Files Valid
- [ ] Deepfake video plays correctly
- [ ] Real video plays correctly
- [ ] Files are MP4 format
- [ ] File sizes are reasonable (<50 MB each)

### Documentation Complete
- [ ] `docs/deepfake_generation.md` - all `_[To be filled]_` sections completed
- [ ] `data/videos/fake/README.md` - status updated, specs filled in
- [ ] `data/videos/real/README.md` - source documented, specs filled in

### Technical Specs Documented
- [ ] Video resolution, duration, codec recorded
- [ ] Generation method and tool documented
- [ ] Source image details provided
- [ ] Real video source and license documented

### Ethical Compliance
- [ ] Ethical statement acknowledged
- [ ] Source materials properly licensed/permitted
- [ ] Academic use only intent documented

---

## Troubleshooting

### Issue: Cannot access Google Flow

**Solution**: Use alternative AI video generation tool
- Update documentation to reflect actual tool used
- Ensure the tool generates a synthetic video suitable for testing

### Issue: Generated video file too large (>50 MB)

**Solution**: Compress the video
```bash
ffmpeg -i large_video.mp4 -vcodec h264 -crf 23 -preset medium \
  -vf scale=-2:720 data/videos/fake/deepfake_inframe_v1.mp4
```
This reduces resolution to 720p and applies compression.

### Issue: Cannot find suitable real video

**Solution**: Record your own
- Use smartphone camera
- 5-10 seconds of yourself talking or moving
- Convert to MP4 if needed

### Issue: Videos different resolutions/framerates

**Solution**: Normalize them
```bash
# Standardize to 720p, 30fps
ffmpeg -i input.mp4 -vf scale=-2:720 -r 30 -c:v h264 -crf 23 output.mp4
```

---

## Getting Help

If you encounter issues:

1. **Check tool documentation**: Google Flow or alternative tool guides
2. **Search for tutorials**: "How to generate deepfake from image"
3. **Use alternative tools**: Many AI video generators exist
4. **Simplify requirements**: Focus on getting *any* synthetic video that works

**Remember**: The goal is to have test videos to evaluate the detection system. The exact tool used is less critical than having suitable test samples.

---

## Next Steps After Completion

Once Phase 2 is complete:

1. **Verify both videos are in repository**
2. **Ensure all documentation is filled in**
3. **Commit and push to GitHub**
4. **Proceed to Phase 3**: Core Development
   - Implement video processing pipeline
   - Integrate LLM API
   - Develop prompt templates
   - Build detection logic

---

## Summary

**You need to**:
1. ✅ Generate deepfake using Google Flow (or alternative)
2. ✅ Acquire authentic real video
3. ✅ Add both videos to repository
4. ✅ Complete documentation templates
5. ✅ Commit and push to GitHub

**I (Claude) have prepared**:
- ✅ Directory structure
- ✅ Documentation templates
- ✅ README files
- ✅ This completion guide

**After you complete the above**, Phase 2 will be done and you can proceed to Phase 3!

---

**Good luck with video generation!**
