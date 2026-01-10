"""
Unit tests for local_agent module.

Tests the local reasoning agent for deepfake detection.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import numpy as np
from pathlib import Path
import yaml
import cv2

from src.local_agent import LocalAgentRunner, LocalAgentProvider


class TestLocalAgentRunnerInitialization:
    """Test LocalAgentRunner initialization."""

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_init_default_version(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test initialization with default version."""
        mock_config.return_value = {
            'agent': {
                'name': 'Test Agent',
                'version': '1.0.0',
                'type': 'local_reasoning'
            }
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        assert agent.agent_version == "v1.0"
        assert mock_config.called
        assert mock_rules.called
        assert mock_templates.called

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_init_custom_version(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test initialization with custom version."""
        mock_config.return_value = {
            'agent': {
                'name': 'Test Agent',
                'version': '2.0.0',
                'type': 'local_reasoning'
            }
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner(agent_version="v2.0")

        assert agent.agent_version == "v2.0"

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_init_sets_attributes(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test that initialization sets all required attributes."""
        test_config = {
            'agent': {
                'name': 'Test Agent',
                'version': '1.0.0',
                'type': 'local_reasoning'
            },
            'deterministic': True,
            'requires_api': False
        }
        mock_config.return_value = test_config
        mock_rules.return_value = {'test': 'rules'}
        mock_templates.return_value = {'test': 'template'}

        agent = LocalAgentRunner()

        assert agent.config == test_config
        assert agent.rules == {'test': 'rules'}
        assert agent.templates == {'test': 'template'}


class TestConfigLoading:
    """Test configuration loading methods."""

    @patch('builtins.open', new_callable=mock_open, read_data='agent:\n  name: Test\n  version: 1.0.0\n  type: local_reasoning')
    @patch('pathlib.Path.exists')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_load_agent_config_success(self, mock_print, mock_templates, mock_rules, mock_exists, mock_file):
        """Test successful agent config loading."""
        mock_exists.return_value = True
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()
        config = agent._load_agent_config()

        assert 'agent' in config
        assert config['agent']['name'] == 'Test'

    @patch('pathlib.Path.exists')
    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_load_agent_config_not_found(self, mock_print, mock_templates, mock_load_config, mock_exists):
        """Test agent config loading when file not found."""
        mock_exists.return_value = False
        mock_load_config.side_effect = FileNotFoundError("Agent definition not found")

        with pytest.raises(FileNotFoundError):
            agent = LocalAgentRunner()

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_get_default_rules(self, mock_print, mock_templates, mock_config):
        """Test default rules generation."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_templates.return_value = {}

        agent = LocalAgentRunner()
        default_rules = agent._get_default_rules()

        assert 'visual_rules' in default_rules
        assert 'temporal_rules' in default_rules
        assert 'confidence_calculation' in default_rules
        assert 'facial_smoothing' in default_rules['visual_rules']
        assert 'motion_continuity' in default_rules['temporal_rules']


class TestVisualArtifactDetection:
    """Test visual artifact detection methods."""

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_detect_visual_artifacts_clean_frame(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test artifact detection on clean frame."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'visual_rules': {
                'facial_smoothing': {'weight': 0.25},
                'lighting_inconsistency': {'weight': 0.20},
                'boundary_artifacts': {'weight': 0.20}
            }
        }
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        # Create a clean frame with high texture variance
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        artifacts = agent._detect_visual_artifacts(frame)

        assert 'facial_smoothing' in artifacts
        assert 'lighting_inconsistency' in artifacts
        assert 'boundary_artifacts' in artifacts
        assert 'total_score' in artifacts
        assert 'findings' in artifacts
        assert isinstance(artifacts['findings'], list)

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_detect_visual_artifacts_smooth_frame(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test artifact detection on overly smooth frame."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'visual_rules': {
                'facial_smoothing': {'weight': 0.25},
                'lighting_inconsistency': {'weight': 0.20},
                'boundary_artifacts': {'weight': 0.20}
            }
        }
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        # Create a smooth frame (low texture variance)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128

        artifacts = agent._detect_visual_artifacts(frame)

        # Smooth frame should have high facial_smoothing score
        assert artifacts['facial_smoothing'] > 0
        assert len(artifacts['findings']) > 0
        assert any('smoothing' in finding.lower() for finding in artifacts['findings'])


class TestFrameAnalysis:
    """Test individual frame analysis."""

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_analyze_frame_structure(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test that analyze_frame returns correct structure."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'visual_rules': {
                'facial_smoothing': {'weight': 0.25},
                'lighting_inconsistency': {'weight': 0.20},
                'boundary_artifacts': {'weight': 0.20}
            }
        }
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        metadata = {'duration': 10.0, 'fps': 30}

        result = agent.analyze_frame(frame, frame_index=5, metadata=metadata)

        assert 'frame_index' in result
        assert 'artifacts_detected' in result
        assert 'analysis' in result
        assert 'artifact_score' in result
        assert result['frame_index'] == 5
        assert isinstance(result['analysis'], str)

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_format_frame_analysis_no_findings(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test frame analysis formatting with no findings."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        artifacts = {'findings': [], 'total_score': 0.0}
        analysis = agent._format_frame_analysis(5, artifacts)

        assert 'Frame 5' in analysis
        assert 'No significant artifacts' in analysis

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_format_frame_analysis_with_findings(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test frame analysis formatting with findings."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        artifacts = {
            'findings': ['Low texture variance detected', 'Uniform lighting detected'],
            'total_score': 0.7
        }
        analysis = agent._format_frame_analysis(5, artifacts)

        assert 'Frame 5' in analysis
        assert 'Low texture variance' in analysis
        assert 'Uniform lighting' in analysis
        assert 'HIGH - suspicious' in analysis or '0.70' in analysis


class TestTemporalAnalysis:
    """Test temporal sequence analysis."""

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_analyze_temporal_sequence_structure(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test temporal analysis returns correct structure."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        # Create sequence of frames
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(5)]
        frame_indices = [0, 5, 10, 15, 20]

        result = agent.analyze_temporal_sequence(frames, frame_indices)

        assert 'num_frames' in result
        assert 'temporal_findings' in result
        assert 'analysis' in result
        assert 'temporal_score' in result
        assert result['num_frames'] == 5
        assert isinstance(result['temporal_findings'], list)

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_analyze_temporal_sequence_identical_frames(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test temporal analysis on identical frames (frozen video)."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        # Create identical frames
        base_frame = np.random.randint(100, 150, (480, 640, 3), dtype=np.uint8)
        frames = [base_frame.copy() for _ in range(3)]
        frame_indices = [0, 1, 2]

        result = agent.analyze_temporal_sequence(frames, frame_indices)

        # Should detect low motion (frozen frames)
        assert result['temporal_score'] > 0 or 'low motion' in result['analysis'].lower()


class TestVerdictSynthesis:
    """Test verdict synthesis."""

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_synthesize_verdict_structure(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test that synthesize_verdict returns correct structure."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'confidence_calculation': {
                'high_confidence_threshold': 0.75,
                'moderate_confidence_threshold': 0.55,
                'uncertain_threshold': 0.45
            }
        }
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        frame_analyses = [
            {
                'frame_index': 0,
                'artifact_score': 0.3,
                'artifacts_detected': {'findings': ['Test finding']}
            },
            {
                'frame_index': 5,
                'artifact_score': 0.2,
                'artifacts_detected': {'findings': []}
            }
        ]

        temporal_analysis = {
            'temporal_findings': ['Test temporal finding'],
            'temporal_score': 0.1,
            'analysis': 'Temporal analysis text'
        }

        metadata = {'duration': 10.0, 'fps': 30}

        result = agent.synthesize_verdict(frame_analyses, temporal_analysis, metadata)

        assert 'classification' in result
        assert 'confidence' in result
        assert 'reasoning' in result
        assert 'evidence' in result
        assert 'scores' in result
        assert isinstance(result['confidence'], int)
        assert result['classification'] in ['FAKE', 'LIKELY FAKE', 'UNCERTAIN', 'LIKELY REAL', 'REAL']

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_synthesize_verdict_high_suspicion(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test verdict synthesis with high suspicion scores."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'confidence_calculation': {
                'high_confidence_threshold': 0.75,
                'moderate_confidence_threshold': 0.55,
                'uncertain_threshold': 0.45
            }
        }
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        # High artifact scores
        frame_analyses = [
            {
                'frame_index': 0,
                'artifact_score': 0.9,
                'artifacts_detected': {'findings': ['High artifacts']}
            },
            {
                'frame_index': 5,
                'artifact_score': 0.8,
                'artifacts_detected': {'findings': ['More artifacts']}
            }
        ]

        temporal_analysis = {
            'temporal_findings': ['Temporal issue'],
            'temporal_score': 0.7,
            'analysis': 'High temporal score'
        }

        metadata = {}

        result = agent.synthesize_verdict(frame_analyses, temporal_analysis, metadata)

        # High suspicion should lead to FAKE classification
        assert result['classification'] in ['FAKE', 'LIKELY FAKE']
        assert result['confidence'] > 50

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_synthesize_verdict_low_suspicion(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test verdict synthesis with low suspicion scores."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'confidence_calculation': {
                'high_confidence_threshold': 0.75,
                'moderate_confidence_threshold': 0.55,
                'uncertain_threshold': 0.45
            }
        }
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        # Low artifact scores
        frame_analyses = [
            {
                'frame_index': 0,
                'artifact_score': 0.1,
                'artifacts_detected': {'findings': []}
            },
            {
                'frame_index': 5,
                'artifact_score': 0.05,
                'artifacts_detected': {'findings': []}
            }
        ]

        temporal_analysis = {
            'temporal_findings': [],
            'temporal_score': 0.0,
            'analysis': 'Clean temporal analysis'
        }

        metadata = {}

        result = agent.synthesize_verdict(frame_analyses, temporal_analysis, metadata)

        # Low suspicion should lead to REAL classification
        assert result['classification'] in ['REAL', 'LIKELY REAL']

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_compile_frame_evidence_empty(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test compiling evidence with no findings."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        frame_analyses = [
            {'frame_index': 0, 'artifacts_detected': {'findings': []}},
            {'frame_index': 5, 'artifacts_detected': {'findings': []}}
        ]

        evidence = agent._compile_frame_evidence(frame_analyses)

        assert 'No significant visual artifacts' in evidence

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_compile_frame_evidence_with_findings(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test compiling evidence with findings."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        frame_analyses = [
            {
                'frame_index': 0,
                'artifacts_detected': {'findings': ['Finding 1', 'Finding 2']}
            },
            {
                'frame_index': 5,
                'artifacts_detected': {'findings': ['Finding 3']}
            }
        ]

        evidence = agent._compile_frame_evidence(frame_analyses)

        assert 'Frame 0' in evidence
        assert 'Frame 5' in evidence
        assert 'Finding 1' in evidence
        assert 'Finding 3' in evidence


class TestLocalAgentProvider:
    """Test LocalAgentProvider wrapper class."""

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_provider_initialization(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test provider initialization."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        provider = LocalAgentProvider(agent_version="v1.0")

        assert provider.agent is not None
        assert isinstance(provider.agent, LocalAgentRunner)
        assert provider.model_name == "local_agent_v1.0"

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_provider_analyze_frame(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test provider analyze_frame delegates to agent."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'visual_rules': {
                'facial_smoothing': {'weight': 0.25},
                'lighting_inconsistency': {'weight': 0.20},
                'boundary_artifacts': {'weight': 0.20}
            }
        }
        mock_templates.return_value = {}

        provider = LocalAgentProvider()

        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        metadata = {}

        result = provider.analyze_frame(frame, frame_index=0, metadata=metadata)

        assert 'frame_index' in result
        assert 'artifacts_detected' in result
        assert 'analysis' in result

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_provider_analyze_temporal_sequence(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test provider analyze_temporal_sequence delegates to agent."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        provider = LocalAgentProvider()

        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(3)]
        frame_indices = [0, 5, 10]

        result = provider.analyze_temporal_sequence(frames, frame_indices)

        assert 'num_frames' in result
        assert 'temporal_findings' in result

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_provider_synthesize_verdict(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test provider synthesize_verdict delegates to agent."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {
            'confidence_calculation': {
                'high_confidence_threshold': 0.75,
                'moderate_confidence_threshold': 0.55,
                'uncertain_threshold': 0.45
            }
        }
        mock_templates.return_value = {}

        provider = LocalAgentProvider()

        frame_analyses = [
            {
                'frame_index': 0,
                'artifact_score': 0.3,
                'artifacts_detected': {'findings': []}
            }
        ]

        temporal_analysis = {
            'temporal_findings': [],
            'temporal_score': 0.1,
            'analysis': 'Test'
        }

        metadata = {}

        result = provider.synthesize_verdict(frame_analyses, temporal_analysis, metadata)

        assert 'classification' in result
        assert 'confidence' in result
        assert 'reasoning' in result


class TestReasoningGeneration:
    """Test reasoning text generation."""

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_generate_reasoning_fake_classification(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test reasoning generation for fake classification."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        frame_analyses = [
            {'frame_index': 0, 'artifacts_detected': {'findings': ['Test finding']}}
        ]

        temporal_analysis = {'temporal_findings': []}

        reasoning = agent._generate_reasoning(
            classification='FAKE',
            confidence=85,
            combined_score=0.8,
            all_findings=['Test finding'],
            frame_analyses=frame_analyses,
            temporal_analysis=temporal_analysis,
            metadata={}
        )

        assert 'FAKE' in reasoning
        assert '85%' in reasoning
        assert 'CONCLUSION' in reasoning
        assert 'synthetic' in reasoning.lower() or 'manipulated' in reasoning.lower()

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_generate_reasoning_real_classification(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test reasoning generation for real classification."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        frame_analyses = [
            {'frame_index': 0, 'artifacts_detected': {'findings': []}}
        ]

        temporal_analysis = {'temporal_findings': []}

        reasoning = agent._generate_reasoning(
            classification='REAL',
            confidence=90,
            combined_score=0.1,
            all_findings=[],
            frame_analyses=frame_analyses,
            temporal_analysis=temporal_analysis,
            metadata={}
        )

        assert 'REAL' in reasoning
        assert '90%' in reasoning
        assert 'CONCLUSION' in reasoning
        assert 'authentic' in reasoning.lower() or 'natural' in reasoning.lower()

    @patch('src.local_agent.LocalAgentRunner._load_agent_config')
    @patch('src.local_agent.LocalAgentRunner._load_detection_rules')
    @patch('src.local_agent.LocalAgentRunner._load_templates')
    @patch('builtins.print')
    def test_generate_reasoning_uncertain_classification(self, mock_print, mock_templates, mock_rules, mock_config):
        """Test reasoning generation for uncertain classification."""
        mock_config.return_value = {
            'agent': {'name': 'Test', 'version': '1.0.0', 'type': 'local_reasoning'}
        }
        mock_rules.return_value = {}
        mock_templates.return_value = {}

        agent = LocalAgentRunner()

        frame_analyses = [
            {'frame_index': 0, 'artifacts_detected': {'findings': ['Ambiguous finding']}}
        ]

        temporal_analysis = {'temporal_findings': []}

        reasoning = agent._generate_reasoning(
            classification='UNCERTAIN',
            confidence=50,
            combined_score=0.5,
            all_findings=['Ambiguous finding'],
            frame_analyses=frame_analyses,
            temporal_analysis=temporal_analysis,
            metadata={}
        )

        assert 'UNCERTAIN' in reasoning
        assert '50%' in reasoning
        assert 'CONCLUSION' in reasoning
        assert 'inconclusive' in reasoning.lower() or 'mixed' in reasoning.lower()
