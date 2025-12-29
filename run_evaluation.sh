#!/bin/bash
# Complete System Evaluation Script
# Run this after adding your API key to .env file

set -e  # Exit on error

echo "======================================================================="
echo "DEEPFAKE DETECTION SYSTEM - FULL EVALUATION"
echo "======================================================================="
echo ""

# Check if API key is configured
if ! grep -q "sk-ant-\|sk-proj-" .env 2>/dev/null; then
    echo "❌ ERROR: API key not configured in .env file"
    echo ""
    echo "Please edit .env and add your Anthropic API key:"
    echo "  ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    exit 1
fi

echo "✅ API key configured"
echo ""

# Create results directory
mkdir -p results

echo "======================================================================="
echo "STEP 1/2: Analyzing DEEPFAKE video"
echo "======================================================================="
echo ""

python detect.py \
  --video data/videos/fake/deepfake_inframe_v1.mp4 \
  --detailed \
  --provider anthropic \
  --output results/deepfake_analysis.json \
  --output-txt results/deepfake_report.txt

echo ""
echo "✅ Deepfake analysis complete"
echo "   Results saved to: results/deepfake_analysis.json"
echo "   Report saved to: results/deepfake_report.txt"
echo ""

echo "======================================================================="
echo "STEP 2/2: Analyzing REAL video"
echo "======================================================================="
echo ""

python detect.py \
  --video data/videos/real/real_video_v1.mp4 \
  --detailed \
  --provider anthropic \
  --output results/real_analysis.json \
  --output-txt results/real_report.txt

echo ""
echo "✅ Real video analysis complete"
echo "   Results saved to: results/real_analysis.json"
echo "   Report saved to: results/real_report.txt"
echo ""

echo "======================================================================="
echo "EVALUATION COMPLETE"
echo "======================================================================="
echo ""
echo "Next steps:"
echo "1. Review the analysis reports in results/"
echo "2. Complete docs/evaluation.md with the actual results"
echo "3. Commit and push all changes"
echo ""
echo "Results summary:"
echo "  - Deepfake: results/deepfake_report.txt"
echo "  - Real:     results/real_report.txt"
echo ""
