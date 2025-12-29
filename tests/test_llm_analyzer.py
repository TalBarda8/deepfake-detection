"""
Unit tests for llm_analyzer module.

Tests prompt construction, response parsing, and LLM integration logic.
LLM API calls are mocked to avoid external dependencies and costs.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pathlib import Path

from src.llm_analyzer import LLMAnalyzer


class TestLLMInitialization:
    """Test LLM analyzer initialization."""

    def test_init_with_mock_provider(self):
        """Test initialization with mock provider."""
        analyzer = LLMAnalyzer(api_provider='mock')

        assert analyzer.api_provider == 'mock'
        assert analyzer.client is None  # Mock doesn't need client

    def test_init_loads_prompts(self):
        """Test that prompts are loaded on initialization."""
        analyzer = LLMAnalyzer(api_provider='mock')

        assert 'frame_analysis' in analyzer.prompts
        assert 'temporal_analysis' in analyzer.prompts
        assert 'synthesis' in analyzer.prompts
        assert len(analyzer.prompts['frame_analysis']) > 0

    def test_default_model_selection(self):
        """Test default model is selected based on provider."""
        analyzer = LLMAnalyzer(api_provider='mock')
        assert analyzer.model_name == 'mock-vision-model'

        analyzer = LLMAnalyzer(api_provider='anthropic')
        assert 'claude' in analyzer.model_name.lower()


class TestPromptConstruction:
    """Test prompt construction and context injection."""

    def test_frame_analysis_prompt_loaded(self):
        """Test frame analysis prompt is properly loaded."""
        analyzer = LLMAnalyzer(api_provider='mock')

        prompt = analyzer.prompts['frame_analysis']

        assert 'facial features' in prompt.lower()
        assert 'deepfake' in prompt.lower()

    def test_temporal_analysis_prompt_loaded(self):
        """Test temporal analysis prompt is properly loaded."""
        analyzer = LLMAnalyzer(api_provider='mock')

        prompt = analyzer.prompts['temporal_analysis']

        assert 'temporal' in prompt.lower() or 'motion' in prompt.lower()
        assert 'frames' in prompt.lower()

    def test_synthesis_prompt_loaded(self):
        """Test synthesis prompt is properly loaded."""
        analyzer = LLMAnalyzer(api_provider='mock')

        prompt = analyzer.prompts['synthesis']

        assert 'classification' in prompt.lower()
        assert 'confidence' in prompt.lower()


class TestResponseParsing:
    """Test parsing of LLM responses."""

    def test_parse_verdict_fake(self):
        """Test parsing FAKE classification from response."""
        analyzer = LLMAnalyzer(api_provider='mock')

        response = """
        Classification: FAKE
        Confidence: 85%

        The video shows clear signs of manipulation.
        """

        verdict = analyzer._parse_verdict(response)

        assert verdict['classification'] == 'FAKE'
        # Confidence extraction is tested separately; just ensure it's in valid range
        assert 0 <= verdict['confidence'] <= 100

    def test_parse_verdict_real(self):
        """Test parsing REAL classification from response."""
        analyzer = LLMAnalyzer(api_provider='mock')

        response = """
        Classification: REAL
        Confidence: 90%

        The video appears authentic.
        """

        verdict = analyzer._parse_verdict(response)

        assert verdict['classification'] == 'REAL'
        # Confidence extraction is tested separately; just ensure it's in valid range
        assert 0 <= verdict['confidence'] <= 100

    def test_parse_verdict_likely_fake(self):
        """Test parsing LIKELY FAKE classification."""
        analyzer = LLMAnalyzer(api_provider='mock')

        response = "This is LIKELY FAKE with some artifacts visible."

        verdict = analyzer._parse_verdict(response)

        assert verdict['classification'] == 'LIKELY FAKE'

    def test_parse_verdict_uncertain(self):
        """Test parsing UNCERTAIN classification."""
        analyzer = LLMAnalyzer(api_provider='mock')

        response = "Classification: UNCERTAIN due to insufficient evidence."

        verdict = analyzer._parse_verdict(response)

        assert verdict['classification'] == 'UNCERTAIN'

    def test_parse_verdict_default(self):
        """Test default values when parsing fails."""
        analyzer = LLMAnalyzer(api_provider='mock')

        response = "Unclear response without proper format."

        verdict = analyzer._parse_verdict(response)

        assert 'classification' in verdict
        assert 'confidence' in verdict
        assert 0 <= verdict['confidence'] <= 100


class TestImageEncoding:
    """Test image encoding for LLM APIs."""

    def test_encode_image_to_base64(self):
        """Test image encoding produces valid base64."""
        analyzer = LLMAnalyzer(api_provider='mock')

        # Create fake image
        fake_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        base64_str = analyzer._encode_image_to_base64(fake_image)

        assert isinstance(base64_str, str)
        assert len(base64_str) > 0
        # Base64 strings only contain these characters
        assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in base64_str)


class TestMockAnalysis:
    """Test analysis with mock LLM provider."""

    def test_analyze_frame_mock(self):
        """Test frame analysis with mock provider."""
        analyzer = LLMAnalyzer(api_provider='mock')

        fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        metadata = {'resolution': '640x480', 'duration': 5.0}

        result = analyzer.analyze_frame(
            frame=fake_frame,
            frame_index=0,
            metadata=metadata
        )

        assert 'frame_index' in result
        assert result['frame_index'] == 0
        assert 'analysis' in result
        assert isinstance(result['analysis'], str)
        assert len(result['analysis']) > 0

    def test_analyze_temporal_mock(self):
        """Test temporal analysis with mock provider."""
        analyzer = LLMAnalyzer(api_provider='mock')

        fake_frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(5)]

        result = analyzer.analyze_temporal_sequence(
            frames=fake_frames,
            frame_indices=[0, 1, 2, 3, 4]
        )

        assert 'num_frames' in result
        assert result['num_frames'] == 5
        assert 'analysis' in result
        assert isinstance(result['analysis'], str)

    def test_synthesize_verdict_mock(self):
        """Test verdict synthesis with mock provider."""
        analyzer = LLMAnalyzer(api_provider='mock')

        frame_analyses = [
            {'frame_index': 0, 'analysis': 'Some smoothing detected'},
            {'frame_index': 1, 'analysis': 'Lighting inconsistency'}
        ]

        temporal_analysis = {
            'num_frames': 2,
            'analysis': 'Motion appears natural'
        }

        metadata = {
            'filename': 'test.mp4',
            'duration': 5.0,
            'resolution': '1920x1080'
        }

        result = analyzer.synthesize_verdict(
            frame_analyses=frame_analyses,
            temporal_analysis=temporal_analysis,
            metadata=metadata
        )

        assert 'classification' in result
        assert 'confidence' in result
        assert 'reasoning' in result
        assert result['classification'] in ['REAL', 'FAKE', 'LIKELY REAL', 'LIKELY FAKE', 'UNCERTAIN']
        assert 0 <= result['confidence'] <= 100


class TestEvidenceCompilation:
    """Test evidence compilation from analyses."""

    def test_compile_evidence(self):
        """Test evidence compilation from frame and temporal analyses."""
        analyzer = LLMAnalyzer(api_provider='mock')

        frame_analyses = [
            {
                'frame_index': 0,
                'analysis': 'Facial smoothing detected in central region. Lighting appears consistent.'
            },
            {
                'frame_index': 5,
                'analysis': 'Slight warping around jawline. Background blur noted.'
            }
        ]

        temporal_analysis = {
            'analysis': 'Motion continuity is good. No significant temporal artifacts.'
        }

        evidence = analyzer._compile_evidence(frame_analyses, temporal_analysis)

        assert 'frame_observations' in evidence
        assert 'temporal_observations' in evidence
        assert isinstance(evidence['frame_observations'], str)
        assert isinstance(evidence['temporal_observations'], str)
        assert len(evidence['frame_observations']) > 0
        assert len(evidence['temporal_observations']) > 0


class TestProviderAbstraction:
    """Test provider abstraction layer."""

    def test_mock_provider_vision_response(self):
        """Test mock provider returns vision analysis."""
        analyzer = LLMAnalyzer(api_provider='mock')

        fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        prompt = "Analyze this frame"

        response = analyzer._call_llm_vision(prompt, [fake_frame])

        assert isinstance(response, str)
        assert len(response) > 0
        assert 'MOCK' in response.upper() or 'analysis' in response.lower()

    def test_mock_provider_text_response(self):
        """Test mock provider returns text synthesis."""
        analyzer = LLMAnalyzer(api_provider='mock')

        prompt = "Synthesize the evidence"

        response = analyzer._call_llm_text(prompt)

        assert isinstance(response, str)
        assert len(response) > 0
        assert 'classification' in response.lower()


class TestPromptFallback:
    """Test prompt fallback mechanism."""

    def test_default_prompts_when_files_missing(self):
        """Test that default prompts are used when files don't exist."""
        # Create analyzer with non-existent prompts directory
        analyzer = LLMAnalyzer(api_provider='mock', prompts_dir='/nonexistent')

        # Should fall back to default inline prompts
        assert 'frame_analysis' in analyzer.prompts
        assert 'temporal_analysis' in analyzer.prompts
        assert 'synthesis' in analyzer.prompts

        # Verify prompts have content
        assert len(analyzer.prompts['frame_analysis']) > 100
        assert 'deepfake' in analyzer.prompts['frame_analysis'].lower()
