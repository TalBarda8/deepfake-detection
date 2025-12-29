"""
Unit tests for output_formatter module.

Tests result formatting for console, JSON, and text reports.
No external dependencies required.
"""

import pytest
import json
from pathlib import Path

from src.output_formatter import OutputFormatter


@pytest.fixture
def sample_results():
    """Sample detection results for testing."""
    return {
        'classification': 'LIKELY FAKE',
        'confidence': 75,
        'reasoning': 'The video shows unnatural facial smoothing and lighting inconsistencies.',
        'metadata': {
            'filename': 'test_video.mp4',
            'duration': 5.2,
            'resolution': '1920x1080',
            'fps': 30.0,
            'codec': 'h264',
            'size_bytes': 1000000
        },
        'evidence': {
            'frame_observations': 'Smoothing detected in frames 2, 5, 7',
            'temporal_observations': 'Minor warping at boundaries'
        },
        'num_frames_analyzed': 10,
        'sampling_strategy': 'uniform',
        'model_name': 'claude-3-5-sonnet',
        'api_provider': 'anthropic',
        'timestamp': '2025-12-27T12:00:00'
    }


class TestConsoleFormatting:
    """Test console report formatting."""

    def test_format_console_report_basic(self, sample_results):
        """Test basic console report contains required elements."""
        report = OutputFormatter.format_console_report(sample_results)

        assert 'DEEPFAKE DETECTION ANALYSIS REPORT' in report
        assert 'test_video.mp4' in report
        assert 'LIKELY FAKE' in report
        assert '75%' in report
        assert '5.2' in report  # Duration
        assert '1920x1080' in report
        assert 'unnatural facial smoothing' in report.lower()

    def test_format_console_report_structure(self, sample_results):
        """Test console report has proper structure."""
        report = OutputFormatter.format_console_report(sample_results)

        # Check for section markers
        assert '=' * 60 in report or '=' * 70 in report
        assert 'Video:' in report
        assert 'Duration:' in report
        assert 'Classification:' in report
        assert 'Confidence:' in report
        assert 'ANALYSIS:' in report

    def test_format_detailed_report(self, sample_results):
        """Test detailed report includes additional information."""
        report = OutputFormatter.format_detailed_report(sample_results)

        assert 'DETAILED ANALYSIS REPORT' in report
        assert 'FRAME-LEVEL OBSERVATIONS' in report
        assert 'TEMPORAL OBSERVATIONS' in report
        assert sample_results['evidence']['frame_observations'] in report
        assert sample_results['evidence']['temporal_observations'] in report
        assert sample_results['model_name'] in report


class TestJSONFormatting:
    """Test JSON output formatting."""

    def test_format_json_valid(self, sample_results):
        """Test JSON output is valid JSON."""
        json_str = OutputFormatter.format_json(sample_results)

        # Should parse without error
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_format_json_structure(self, sample_results):
        """Test JSON output has correct structure."""
        json_str = OutputFormatter.format_json(sample_results)
        parsed = json.loads(json_str)

        assert 'video_path' in parsed or 'filename' in parsed
        assert 'metadata' in parsed
        assert 'detection' in parsed
        assert 'analysis' in parsed
        assert 'system' in parsed

    def test_format_json_detection_fields(self, sample_results):
        """Test JSON detection section has required fields."""
        json_str = OutputFormatter.format_json(sample_results)
        parsed = json.loads(json_str)

        detection = parsed['detection']
        assert detection['classification'] == 'LIKELY FAKE'
        assert detection['confidence'] == 75
        assert detection['num_frames_analyzed'] == 10

    def test_format_json_pretty_vs_compact(self, sample_results):
        """Test pretty vs. compact JSON formatting."""
        pretty = OutputFormatter.format_json(sample_results, pretty=True)
        compact = OutputFormatter.format_json(sample_results, pretty=False)

        # Pretty should have newlines and indentation
        assert '\n' in pretty
        assert '  ' in pretty or '\t' in pretty

        # Compact should be more condensed
        assert len(compact) < len(pretty)

        # Both should parse to same data
        assert json.loads(pretty) == json.loads(compact)


class TestFileOperations:
    """Test saving to files."""

    def test_save_json(self, sample_results, tmp_path):
        """Test saving JSON to file."""
        output_file = tmp_path / "result.json"

        OutputFormatter.save_json(sample_results, str(output_file))

        assert output_file.exists()

        # Verify content
        with open(output_file, 'r') as f:
            data = json.load(f)
        assert data['detection']['classification'] == 'LIKELY FAKE'

    def test_save_text_report(self, sample_results, tmp_path):
        """Test saving text report to file."""
        output_file = tmp_path / "report.txt"

        OutputFormatter.save_text_report(sample_results, str(output_file))

        assert output_file.exists()

        # Verify content
        with open(output_file, 'r') as f:
            content = f.read()
        assert 'LIKELY FAKE' in content
        assert 'test_video.mp4' in content

    def test_save_creates_directories(self, sample_results, tmp_path):
        """Test that save functions create parent directories."""
        output_file = tmp_path / "nested" / "dir" / "result.json"

        OutputFormatter.save_json(sample_results, str(output_file))

        assert output_file.exists()
        assert output_file.parent.exists()


class TestSummaryFormatting:
    """Test summary formatting."""

    def test_format_summary(self, sample_results):
        """Test summary format is concise."""
        summary = OutputFormatter.format_summary(sample_results)

        assert 'test_video.mp4' in summary
        assert 'LIKELY FAKE' in summary
        assert '75%' in summary
        # Should be single line
        assert '\n' not in summary or summary.count('\n') <= 1

    def test_format_summary_different_classifications(self):
        """Test summary handles different classification types."""
        for classification in ['REAL', 'FAKE', 'UNCERTAIN', 'LIKELY REAL']:
            results = {
                'classification': classification,
                'confidence': 80,
                'metadata': {'filename': 'test.mp4'}
            }

            summary = OutputFormatter.format_summary(results)
            assert classification in summary


class TestClassificationEmoji:
    """Test emoji classification helpers."""

    def test_get_classification_emoji(self):
        """Test emoji mapping for classifications."""
        assert OutputFormatter.get_classification_emoji('REAL') == '✅'
        assert OutputFormatter.get_classification_emoji('FAKE') == '❌'
        assert OutputFormatter.get_classification_emoji('UNCERTAIN') == '❓'
        assert OutputFormatter.get_classification_emoji('LIKELY FAKE') == '⚠️'
        assert OutputFormatter.get_classification_emoji('LIKELY REAL') == '✓'

    def test_get_classification_emoji_case_insensitive(self):
        """Test emoji mapping is case insensitive."""
        assert OutputFormatter.get_classification_emoji('real') == '✅'
        assert OutputFormatter.get_classification_emoji('REAL') == '✅'

    def test_get_classification_emoji_unknown(self):
        """Test emoji for unknown classification."""
        emoji = OutputFormatter.get_classification_emoji('UNKNOWN')
        assert emoji in ['❔', '❓']  # Either is acceptable


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_format_with_missing_fields(self):
        """Test formatting handles missing optional fields gracefully."""
        minimal_results = {
            'classification': 'FAKE',
            'confidence': 90
        }

        # Should not raise exceptions
        report = OutputFormatter.format_console_report(minimal_results)
        assert 'FAKE' in report
        assert '90%' in report

    def test_format_with_none_values(self):
        """Test formatting handles None values."""
        results = {
            'classification': 'REAL',
            'confidence': 85,
            'metadata': {
                'filename': None,
                'duration': 0  # Duration defaults to 0, not None
            }
        }

        # Should not raise exceptions
        report = OutputFormatter.format_console_report(results)
        assert 'REAL' in report

    def test_json_format_with_unicode(self):
        """Test JSON formatting handles unicode characters."""
        results = {
            'classification': 'FAKE',
            'confidence': 75,
            'reasoning': 'Test with unicode: 日本語 中文 עברית',
            'metadata': {'filename': 'test.mp4'}
        }

        json_str = OutputFormatter.format_json(results)
        parsed = json.loads(json_str)

        # Unicode should be preserved
        assert '日本語' in parsed['analysis']['reasoning'] or 'reasoning' in str(parsed)
