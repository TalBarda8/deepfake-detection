# Final Evaluation Setup Guide

**Status**: All videos organized and ready. API key configuration required to complete evaluation.

## What's Been Completed ✅

1. **Deepfake Video**: Organized at `data/videos/fake/deepfake_inframe_v1.mp4`
   - File size: 1.2 MB
   - Duration: ~21 seconds
   - Generated: December 29, 2025 using Google Flow Inframe

2. **Real Video**: Organized at `data/videos/real/real_video_v1.mp4`
   - File size: 8.5 MB
   - Duration: 21.0 seconds
   - Resolution: 1080x1920 (portrait)
   - Frame rate: 29.97 fps
   - Source: Vecteezy stock footage

3. **Results Directory**: Created at `results/`

4. **Evaluation Script**: `run_evaluation.sh` (executable)

5. **Documentation**: Updated README files in both video directories

## What You Need to Do

### Step 1: Add Your Anthropic API Key

Edit the `.env` file and add your actual API key:

```bash
nano .env
```

Replace `your_anthropic_api_key_here` with your actual key from https://console.anthropic.com/

The `.env` file should look like:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Step 2: Run the Full Evaluation

Option A - Use the helper script:
```bash
./run_evaluation.sh
```

Option B - Run commands manually:
```bash
# Analyze deepfake video
python detect.py \
  --video data/videos/fake/deepfake_inframe_v1.mp4 \
  --detailed \
  --provider anthropic \
  --output results/deepfake_analysis.json \
  --output-txt results/deepfake_report.txt

# Analyze real video
python detect.py \
  --video data/videos/real/real_video_v1.mp4 \
  --detailed \
  --provider anthropic \
  --output results/real_analysis.json \
  --output-txt results/real_report.txt
```

### Step 3: Review Results

After running the evaluation, you'll have:

- `results/deepfake_analysis.json` - Structured JSON output for deepfake
- `results/deepfake_report.txt` - Detailed text report for deepfake
- `results/real_analysis.json` - Structured JSON output for real video
- `results/real_report.txt` - Detailed text report for real video

### Step 4: Complete docs/evaluation.md

Use the actual outputs to fill in all sections of `docs/evaluation.md`:

1. Copy real metadata from ffprobe outputs and JSON results
2. Paste actual LLM reasoning from the text reports
3. Write comparative analysis based on observed differences
4. Document limitations and edge cases you notice
5. Add academic reflection on the approach

### Step 5: Commit Final Results

```bash
git add results/ docs/evaluation.md .env
git commit -m "Complete real vs deepfake evaluation with actual results"
git push
```

**Note**: The `.env` file is in `.gitignore` so your API key won't be committed.

## Expected Timeline

- Step 1 (API key): 2 minutes
- Step 2 (Run evaluation): 5-10 minutes (depends on video length and API speed)
- Step 3 (Review): 5 minutes
- Step 4 (Complete docs/evaluation.md): 30-60 minutes
- Step 5 (Commit): 2 minutes

**Total**: ~45-80 minutes to complete full evaluation

## Troubleshooting

### "Could not resolve authentication method"
- Your API key is not set correctly in `.env`
- Make sure you copied the full key starting with `sk-ant-`
- No spaces around the `=` sign

### "API rate limit exceeded"
- Wait a few minutes and try again
- Consider reducing the number of frames with `--frames 5`

### "Module not found: cv2"
- Install opencv: `pip install opencv-python`

### "FFmpeg not found"
- Install ffmpeg: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

## Alternative: Using OpenAI GPT-4V

If you prefer to use OpenAI instead:

1. Add `OPENAI_API_KEY` to `.env` instead of ANTHROPIC_API_KEY
2. Use `--provider openai` in the commands above

## Files Generated

```
results/
├── deepfake_analysis.json     # Structured results for fake video
├── deepfake_report.txt         # Detailed text report for fake video
├── real_analysis.json          # Structured results for real video
└── real_report.txt             # Detailed text report for real video
```

These files will contain:
- Classification (REAL/FAKE/UNCERTAIN/etc.)
- Confidence score (0-100%)
- Detailed reasoning and observations
- Frame-by-frame analysis notes
- Temporal consistency observations
- Evidence summary

---

**Once you've completed all steps, the project will be ready for final academic submission!**
