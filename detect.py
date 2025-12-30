#!/usr/bin/env python3
"""
Deepfake Detection CLI

Command-line interface for the LLM-based deepfake detection system.

Usage:
    python detect.py --video path/to/video.mp4
    python detect.py --video path/to/video.mp4 --output results.json
    python detect.py --batch path/to/videos/*.mp4 --output-dir results/
"""

import argparse
import sys
from pathlib import Path
import logging

from src.detector import DeepfakeDetector, create_detector
from src.output_formatter import OutputFormatter


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="LLM-based Deepfake Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single video
  python detect.py --video data/videos/fake/deepfake_inframe_v1.mp4

  # Analyze with custom settings
  python detect.py --video video.mp4 --frames 15 --model gpt-4o

  # Enable parallel processing for faster frame extraction (2-4x speedup)
  python detect.py --video video.mp4 --parallel --workers 4

  # Save results to JSON
  python detect.py --video video.mp4 --output results/analysis.json

  # Use mock mode for testing (no API calls)
  python detect.py --video video.mp4 --provider mock

  # Batch processing with parallel processing
  python detect.py --batch data/videos/fake/*.mp4 --output-dir results/ --parallel

Supported Providers:
  - local: Self-contained reasoning agent (default, no API required)
  - anthropic: Claude 3.5 Sonnet (requires API key)
  - openai: GPT-4 with vision (requires API key)
  - mock: Testing mode without API calls

Environment Variables (optional):
  ANTHROPIC_API_KEY: API key for Anthropic (Claude) - only if using --provider anthropic
  OPENAI_API_KEY: API key for OpenAI (GPT-4) - only if using --provider openai
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--video', '-v',
        type=str,
        help='Path to video file to analyze'
    )
    input_group.add_argument(
        '--batch', '-b',
        type=str,
        nargs='+',
        help='Paths to multiple videos for batch processing'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to save JSON results (optional)'
    )
    parser.add_argument(
        '--output-txt',
        type=str,
        help='Path to save text report (optional)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory to save batch results (for --batch mode)'
    )

    # Detection options
    parser.add_argument(
        '--provider', '-p',
        type=str,
        choices=['local', 'anthropic', 'openai', 'mock'],
        default='local',
        help='Analysis provider to use (default: local)'
    )
    parser.add_argument(
        '--model', '-m',
        type=str,
        help='Specific model name (optional, uses provider default)'
    )
    parser.add_argument(
        '--frames', '-f',
        type=int,
        default=10,
        help='Number of frames to extract (default: 10)'
    )
    parser.add_argument(
        '--sampling',
        type=str,
        choices=['uniform', 'keyframes', 'adaptive'],
        default='uniform',
        help='Frame sampling strategy (default: uniform)'
    )
    parser.add_argument(
        '--prompts-dir',
        type=str,
        default='prompts',
        help='Directory containing prompt templates (default: prompts)'
    )

    # Performance options
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel processing for faster frame extraction (2-4x speedup)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        help='Number of parallel workers (default: auto-detect based on CPU cores)'
    )

    # Display options
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed analysis report'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress console output (still saves files if specified)'
    )

    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()

    # Setup logging
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    logger = logging.getLogger('detect')

    # Create detector
    try:
        detector = create_detector(
            api_provider=args.provider,
            model_name=args.model,
            num_frames=args.frames,
            sampling_strategy=args.sampling,
            prompts_dir=args.prompts_dir,
            verbose=args.verbose,
            use_parallel=args.parallel,
            max_workers=args.workers
        )
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        sys.exit(1)

    # Single video mode
    if args.video:
        try:
            results = detector.detect(args.video)

            # Print to console unless quiet mode
            if not args.quiet:
                OutputFormatter.print_console_report(results, detailed=args.detailed)

            # Save JSON if requested
            if args.output:
                OutputFormatter.save_json(results, args.output)
                logger.info(f"Saved JSON results to: {args.output}")

            # Save text report if requested
            if args.output_txt:
                OutputFormatter.save_text_report(results, args.output_txt, detailed=args.detailed)
                logger.info(f"Saved text report to: {args.output_txt}")

            # Exit with appropriate code
            classification = results.get('classification', 'UNKNOWN')
            if classification in ['FAKE', 'LIKELY FAKE']:
                sys.exit(1)  # Detected as fake
            elif classification in ['REAL', 'LIKELY REAL']:
                sys.exit(0)  # Detected as real
            else:
                sys.exit(2)  # Uncertain

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            sys.exit(3)

    # Batch mode
    elif args.batch:
        try:
            # Expand paths
            video_paths = []
            for pattern in args.batch:
                # Handle glob patterns
                if '*' in pattern or '?' in pattern:
                    from glob import glob
                    video_paths.extend(glob(pattern))
                else:
                    video_paths.append(pattern)

            if not video_paths:
                logger.error("No videos found matching the specified patterns")
                sys.exit(1)

            logger.info(f"Processing {len(video_paths)} videos...")

            # Process batch
            results = detector.batch_detect(
                video_paths=video_paths,
                output_dir=args.output_dir
            )

            # Print summary
            if not args.quiet:
                print("\n" + "=" * 70)
                print("BATCH PROCESSING SUMMARY")
                print("=" * 70)

                for video_path, result in results.items():
                    print(OutputFormatter.format_summary(result))

                print("=" * 70)

                # Statistics
                total = len(results)
                fake_count = sum(1 for r in results.values()
                               if r.get('classification', '').upper() in ['FAKE', 'LIKELY FAKE'])
                real_count = sum(1 for r in results.values()
                               if r.get('classification', '').upper() in ['REAL', 'LIKELY REAL'])
                uncertain_count = sum(1 for r in results.values()
                                    if r.get('classification', '').upper() == 'UNCERTAIN')
                error_count = sum(1 for r in results.values()
                                if r.get('classification', '').upper() == 'ERROR')

                print(f"\nTotal: {total}")
                print(f"Fake/Likely Fake: {fake_count}")
                print(f"Real/Likely Real: {real_count}")
                print(f"Uncertain: {uncertain_count}")
                print(f"Errors: {error_count}")

            if args.output_dir:
                logger.info(f"Results saved to: {args.output_dir}")

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            sys.exit(3)


if __name__ == '__main__':
    main()
