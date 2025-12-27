"""
Output Formatter Module

Handles formatting and display of detection results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class OutputFormatter:
    """
    Formats and displays deepfake detection results.

    Provides console output and JSON export capabilities.
    """

    @staticmethod
    def format_console_report(results: Dict[str, Any]) -> str:
        """
        Format results as a console-friendly report.

        Args:
            results: Detection results dictionary

        Returns:
            Formatted report string
        """
        classification = results.get('classification', 'UNKNOWN')
        confidence = results.get('confidence', 0)
        metadata = results.get('metadata', {})
        reasoning = results.get('reasoning', 'No reasoning provided')

        # Build report
        report_lines = [
            "=" * 70,
            "DEEPFAKE DETECTION ANALYSIS REPORT",
            "=" * 70,
            "",
            f"Video: {metadata.get('filename', 'Unknown')}",
            f"Duration: {metadata.get('duration', 0):.2f}s",
            f"Resolution: {metadata.get('resolution', 'Unknown')}",
            f"Frames Analyzed: {results.get('num_frames_analyzed', 0)}",
            "",
            f"Classification: {classification}",
            f"Confidence: {confidence}%",
            "",
            "ANALYSIS:",
            "",
            reasoning,
            "",
            "=" * 70,
            f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70
        ]

        return "\n".join(report_lines)

    @staticmethod
    def format_detailed_report(results: Dict[str, Any]) -> str:
        """
        Format results as a detailed report with all evidence.

        Args:
            results: Detection results dictionary

        Returns:
            Detailed formatted report
        """
        classification = results.get('classification', 'UNKNOWN')
        confidence = results.get('confidence', 0)
        metadata = results.get('metadata', {})
        reasoning = results.get('reasoning', 'No reasoning provided')
        evidence = results.get('evidence', {})

        # Build detailed report
        report_lines = [
            "=" * 70,
            "DEEPFAKE DETECTION - DETAILED ANALYSIS REPORT",
            "=" * 70,
            "",
            "VIDEO INFORMATION",
            "-" * 70,
            f"Filename: {metadata.get('filename', 'Unknown')}",
            f"Path: {metadata.get('path', 'Unknown')}",
            f"Duration: {metadata.get('duration', 0):.2f} seconds",
            f"Resolution: {metadata.get('resolution', 'Unknown')}",
            f"Frame Rate: {metadata.get('fps', 0):.2f} fps",
            f"Codec: {metadata.get('codec', 'Unknown')}",
            f"File Size: {metadata.get('size_bytes', 0) / 1024 / 1024:.2f} MB",
            "",
            "DETECTION RESULTS",
            "-" * 70,
            f"Classification: {classification}",
            f"Confidence Level: {confidence}%",
            f"Frames Analyzed: {results.get('num_frames_analyzed', 0)}",
            f"Sampling Strategy: {results.get('sampling_strategy', 'Unknown')}",
            "",
            "FRAME-LEVEL OBSERVATIONS",
            "-" * 70,
            evidence.get('frame_observations', 'No frame observations available'),
            "",
            "TEMPORAL OBSERVATIONS",
            "-" * 70,
            evidence.get('temporal_observations', 'No temporal observations available'),
            "",
            "FINAL REASONING",
            "-" * 70,
            reasoning,
            "",
            "=" * 70,
            f"Model Used: {results.get('model_name', 'Unknown')}",
            f"Analysis Timestamp: {results.get('timestamp', datetime.now().isoformat())}",
            "=" * 70
        ]

        return "\n".join(report_lines)

    @staticmethod
    def format_json(results: Dict[str, Any], pretty: bool = True) -> str:
        """
        Format results as JSON.

        Args:
            results: Detection results dictionary
            pretty: Whether to pretty-print JSON

        Returns:
            JSON string
        """
        # Create JSON-serializable copy
        json_results = {
            'video_path': results.get('metadata', {}).get('path', ''),
            'filename': results.get('metadata', {}).get('filename', ''),
            'metadata': results.get('metadata', {}),
            'detection': {
                'classification': results.get('classification', 'UNKNOWN'),
                'confidence': results.get('confidence', 0),
                'num_frames_analyzed': results.get('num_frames_analyzed', 0),
                'sampling_strategy': results.get('sampling_strategy', 'unknown')
            },
            'analysis': {
                'reasoning': results.get('reasoning', ''),
                'evidence': results.get('evidence', {})
            },
            'system': {
                'model_name': results.get('model_name', 'unknown'),
                'api_provider': results.get('api_provider', 'unknown'),
                'timestamp': results.get('timestamp', datetime.now().isoformat())
            }
        }

        if pretty:
            return json.dumps(json_results, indent=2, ensure_ascii=False)
        else:
            return json.dumps(json_results, ensure_ascii=False)

    @staticmethod
    def save_json(results: Dict[str, Any], output_path: str) -> None:
        """
        Save results to JSON file.

        Args:
            results: Detection results dictionary
            output_path: Path to save JSON file
        """
        json_str = OutputFormatter.format_json(results, pretty=True)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_str)

    @staticmethod
    def save_text_report(results: Dict[str, Any], output_path: str, detailed: bool = True) -> None:
        """
        Save results to text report file.

        Args:
            results: Detection results dictionary
            output_path: Path to save text file
            detailed: Whether to use detailed format
        """
        if detailed:
            report = OutputFormatter.format_detailed_report(results)
        else:
            report = OutputFormatter.format_console_report(results)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

    @staticmethod
    def print_console_report(results: Dict[str, Any], detailed: bool = False) -> None:
        """
        Print results to console.

        Args:
            results: Detection results dictionary
            detailed: Whether to use detailed format
        """
        if detailed:
            report = OutputFormatter.format_detailed_report(results)
        else:
            report = OutputFormatter.format_console_report(results)

        print(report)

    @staticmethod
    def get_classification_emoji(classification: str) -> str:
        """
        Get emoji representation of classification.

        Args:
            classification: Classification string

        Returns:
            Emoji string
        """
        emojis = {
            'REAL': '✅',
            'FAKE': '❌',
            'LIKELY REAL': '✓',
            'LIKELY FAKE': '⚠️',
            'UNCERTAIN': '❓',
            'UNKNOWN': '❔'
        }

        return emojis.get(classification.upper(), '❔')

    @staticmethod
    def format_summary(results: Dict[str, Any]) -> str:
        """
        Format a brief summary line.

        Args:
            results: Detection results dictionary

        Returns:
            Summary string
        """
        classification = results.get('classification', 'UNKNOWN')
        confidence = results.get('confidence', 0)
        filename = results.get('metadata', {}).get('filename', 'Unknown')

        emoji = OutputFormatter.get_classification_emoji(classification)

        return f"{emoji} {filename}: {classification} ({confidence}% confidence)"
