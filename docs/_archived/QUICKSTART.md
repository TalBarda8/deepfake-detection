# Quick Start Guide

Get the deepfake detection system running in 5 minutes.

## Prerequisites

- Python 3.9+
- FFmpeg (for video processing)
- API key (Anthropic or OpenAI) OR use mock mode

## Installation

### 1. Install FFmpeg

**macOS**:
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows**:
Download from https://ffmpeg.org/download.html

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python test_imports.py
```

You should see checkmarks for all required dependencies.

## Configuration

### Option 1: Mock Mode (No API Key Required)

Test the system without API calls:

```bash
python detect.py --video <path-to-video.mp4> --provider mock
```

### Option 2: Real API (Anthropic or OpenAI)

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   # OR
   OPENAI_API_KEY=your_key_here
   ```

3. Run detection:
   ```bash
   # Using Anthropic (Claude)
   python detect.py --video <path-to-video.mp4>

   # Using OpenAI (GPT-4)
   python detect.py --video <path-to-video.mp4> --provider openai
   ```

## First Test

Once videos are added to the repository, test the system:

```bash
# Test with mock mode (no API cost)
python detect.py --video data/videos/fake/deepfake_inframe_v1.mp4 --provider mock

# Test with real API
python detect.py --video data/videos/fake/deepfake_inframe_v1.mp4
```

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'cv2'`
**Solution**: `pip install opencv-python`

**Issue**: `ffprobe: command not found`
**Solution**: Install FFmpeg (see step 1)

**Issue**: `Video file not found`
**Solution**: Ensure you've added test videos to `data/videos/`

**Issue**: API key errors
**Solution**: Check `.env` file has correct key without quotes

## Next Steps

- Read [README.md](README.md) for full documentation
- See [docs/detection_agent.md](docs/detection_agent.md) for system details
- Add your own test videos to `data/videos/`

## Quick Command Reference

```bash
# Basic analysis
python detect.py --video <video.mp4>

# Save results
python detect.py --video <video.mp4> --output results.json

# Detailed report
python detect.py --video <video.mp4> --detailed

# Batch processing
python detect.py --batch data/videos/*/*.mp4 --output-dir results/

# Custom frame count
python detect.py --video <video.mp4> --frames 15

# Verbose logging
python detect.py --video <video.mp4> --verbose
```

## Getting Help

Run `python detect.py --help` for all available options.

Happy detecting!
