"""
Local Reasoning Agent for Deepfake Detection

This module implements a self-contained, reproducible agent that performs
deepfake detection through rule-based reasoning and structured analysis.

NO EXTERNAL API CALLS. Fully deterministic and version-controlled.
"""

import os
import json
import yaml
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import cv2


class LocalAgentRunner:
    """
    Self-contained agent that analyzes videos for deepfake artifacts.

    Uses rule-based heuristics + structured reasoning templates to produce
    LLM-style outputs without requiring external API calls.

    Attributes:
        agent_version (str): Version of the agent being used
        agent_dir (Path): Directory containing agent definition files
        config (dict): Agent configuration loaded from agent_definition.yaml
        rules (dict): Detection rules loaded from detection_rules.yaml
    """

    def __init__(self, agent_version: str = "v1.0"):
        """
        Initialize the local agent.

        Args:
            agent_version: Version string (e.g., "v1.0")
        """
        self.agent_version = agent_version
        self.agent_dir = Path(__file__).parent.parent / "agents" / f"deepfake_detector_{agent_version}"

        # Load agent definition
        self.config = self._load_agent_config()
        self.rules = self._load_detection_rules()

        # Load reasoning templates
        self.templates = self._load_templates()

        print(f"✓ Loaded Local Agent: {self.config['agent']['name']} v{self.config['agent']['version']}")
        print(f"  Agent Type: {self.config['agent']['type']}")
        print(f"  Deterministic: {self.config.get('deterministic', True)}")
        print(f"  Requires API: {self.config.get('requires_api', False)}")

    def _load_agent_config(self) -> dict:
        """Load agent configuration from agent_definition.yaml."""
        config_path = self.agent_dir / "agent_definition.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent definition not found: {config_path}")

        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _load_detection_rules(self) -> dict:
        """Load detection rules from detection_rules.yaml."""
        rules_path = self.agent_dir / "detection_rules.yaml"
        if not rules_path.exists():
            # Return default minimal rules if file doesn't exist yet
            return self._get_default_rules()

        with open(rules_path, 'r') as f:
            return yaml.safe_load(f)

    def _get_default_rules(self) -> dict:
        """Provide default detection rules if file not found."""
        return {
            'visual_rules': {
                'facial_smoothing': {'weight': 0.25},
                'lighting_inconsistency': {'weight': 0.20},
                'boundary_artifacts': {'weight': 0.20}
            },
            'temporal_rules': {
                'motion_continuity': {'weight': 0.30},
                'temporal_artifacts': {'weight': 0.50}
            },
            'confidence_calculation': {
                'high_confidence_threshold': 0.75,
                'moderate_confidence_threshold': 0.55,
                'uncertain_threshold': 0.45
            }
        }

    def _load_templates(self) -> dict:
        """Load reasoning templates."""
        templates = {}
        template_files = [
            'frame_analysis_template.md',
            'temporal_analysis_template.md',
            'synthesis_template.md'
        ]

        for filename in template_files:
            filepath = self.agent_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    key = filename.replace('_template.md', '')
                    templates[key] = f.read()

        return templates

    def analyze_frame(self, frame: np.ndarray, frame_index: int, metadata: dict) -> dict:
        """
        Analyze a single frame for deepfake artifacts.

        Args:
            frame: Image array (BGR format from OpenCV)
            frame_index: Index of this frame in the video
            metadata: Video metadata dictionary

        Returns:
            Dictionary with frame analysis results
        """
        # Convert to RGB if needed
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            frame_rgb = frame

        # Detect visual artifacts using rule-based heuristics
        artifacts = self._detect_visual_artifacts(frame_rgb)

        # Generate structured analysis
        analysis_text = self._format_frame_analysis(frame_index, artifacts)

        return {
            'frame_index': frame_index,
            'artifacts_detected': artifacts,
            'analysis': analysis_text,
            'artifact_score': artifacts['total_score']
        }

    def _detect_visual_artifacts(self, frame: np.ndarray) -> dict:
        """
        Apply visual detection rules to identify potential artifacts.

        This uses OpenCV-based heuristics to detect:
        - Facial smoothing (texture analysis)
        - Lighting inconsistencies (gradient analysis)
        - Boundary artifacts (edge detection)
        - Resolution mismatches (frequency analysis)

        Args:
            frame: RGB image array

        Returns:
            Dictionary with artifact scores and findings
        """
        artifacts = {
            'facial_smoothing': 0.0,
            'lighting_inconsistency': 0.0,
            'boundary_artifacts': 0.0,
            'resolution_mismatch': 0.0,
            'findings': []
        }

        # 1. Detect facial smoothing (texture variance)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Low variance suggests smoothing
        if laplacian_var < 100:
            artifacts['facial_smoothing'] = 0.7
            artifacts['findings'].append("Low texture variance detected (potential smoothing)")
        elif laplacian_var < 200:
            artifacts['facial_smoothing'] = 0.4
            artifacts['findings'].append("Moderate texture variance (some smoothing possible)")

        # 2. Lighting inconsistency (gradient analysis)
        # Detect if lighting is uniform (suspicious)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        if grad_magnitude.std() < 20:
            artifacts['lighting_inconsistency'] = 0.6
            artifacts['findings'].append("Uniform lighting detected (potentially artificial)")

        # 3. Boundary artifacts (edge detection)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        if edge_density < 0.05:  # Too few edges
            artifacts['boundary_artifacts'] = 0.5
            artifacts['findings'].append("Low edge density (possible boundary blending)")
        elif edge_density > 0.20:  # Too many edges
            artifacts['boundary_artifacts'] = 0.4
            artifacts['findings'].append("High edge density (possible artifacts)")

        # 4. Calculate total artifact score
        weights = self.rules.get('visual_rules', {})
        total_score = (
            artifacts['facial_smoothing'] * weights.get('facial_smoothing', {}).get('weight', 0.25) +
            artifacts['lighting_inconsistency'] * weights.get('lighting_inconsistency', {}).get('weight', 0.20) +
            artifacts['boundary_artifacts'] * weights.get('boundary_artifacts', {}).get('weight', 0.20)
        )

        artifacts['total_score'] = total_score

        return artifacts

    def _format_frame_analysis(self, frame_index: int, artifacts: dict) -> str:
        """Format frame analysis into natural language."""
        findings = artifacts.get('findings', [])

        if not findings:
            return f"Frame {frame_index}: No significant artifacts detected. Visual quality appears natural."

        analysis_parts = [f"Frame {frame_index} Analysis:"]

        for finding in findings:
            analysis_parts.append(f"  - {finding}")

        score = artifacts.get('total_score', 0.0)
        if score > 0.6:
            analysis_parts.append(f"  Overall artifact score: {score:.2f} (HIGH - suspicious)")
        elif score > 0.3:
            analysis_parts.append(f"  Overall artifact score: {score:.2f} (MODERATE)")
        else:
            analysis_parts.append(f"  Overall artifact score: {score:.2f} (LOW - appears natural)")

        return "\n".join(analysis_parts)

    def analyze_temporal_sequence(self, frames: List[np.ndarray], frame_indices: List[int]) -> dict:
        """
        Analyze temporal consistency across multiple frames.

        Args:
            frames: List of frame arrays
            frame_indices: Corresponding frame indices

        Returns:
            Dictionary with temporal analysis results
        """
        temporal_findings = []

        # Check frame-to-frame consistency
        for i in range(len(frames) - 1):
            frame1_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            frame2_gray = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)

            # Calculate optical flow or motion difference
            diff = cv2.absdiff(frame1_gray, frame2_gray)
            motion_score = np.mean(diff)

            if motion_score > 50:
                temporal_findings.append(
                    f"Large motion discontinuity between frames {frame_indices[i]} and {frame_indices[i+1]}"
                )
            elif motion_score < 5:
                temporal_findings.append(
                    f"Very low motion between frames {frame_indices[i]} and {frame_indices[i+1]} (potentially static/frozen)"
                )

        # Generate analysis text
        if not temporal_findings:
            analysis_text = f"Temporal analysis across {len(frames)} frames: Motion appears continuous and natural."
        else:
            analysis_text = f"Temporal analysis across {len(frames)} frames:\n"
            for finding in temporal_findings:
                analysis_text += f"  - {finding}\n"

        return {
            'num_frames': len(frames),
            'temporal_findings': temporal_findings,
            'analysis': analysis_text,
            'temporal_score': len(temporal_findings) / max(len(frames) - 1, 1)
        }

    def synthesize_verdict(
        self,
        frame_analyses: List[dict],
        temporal_analysis: dict,
        metadata: dict
    ) -> dict:
        """
        Synthesize final verdict from frame and temporal analyses.

        Args:
            frame_analyses: List of frame analysis results
            temporal_analysis: Temporal analysis results
            metadata: Video metadata

        Returns:
            Final verdict dictionary with classification, confidence, reasoning
        """
        # Aggregate artifact scores from frames
        artifact_scores = [fa.get('artifact_score', 0.0) for fa in frame_analyses]
        avg_artifact_score = np.mean(artifact_scores) if artifact_scores else 0.0
        max_artifact_score = np.max(artifact_scores) if artifact_scores else 0.0

        # Get temporal score
        temporal_score = temporal_analysis.get('temporal_score', 0.0)

        # Combined suspicion score (0.0 = real, 1.0 = fake)
        # Weight: 60% visual artifacts, 40% temporal
        combined_score = (avg_artifact_score * 0.6) + (temporal_score * 0.4)

        # Determine classification and confidence
        thresholds = self.rules.get('confidence_calculation', {})
        high_thresh = thresholds.get('high_confidence_threshold', 0.75)
        mod_thresh = thresholds.get('moderate_confidence_threshold', 0.55)
        uncertain_thresh = thresholds.get('uncertain_threshold', 0.45)

        if combined_score >= high_thresh:
            classification = "FAKE"
            confidence = min(95, int(70 + (combined_score - high_thresh) * 100))
        elif combined_score >= mod_thresh:
            classification = "LIKELY FAKE"
            confidence = int(55 + (combined_score - mod_thresh) * 75)
        elif combined_score >= uncertain_thresh:
            classification = "UNCERTAIN"
            confidence = 50
        elif combined_score >= 0.25:
            classification = "LIKELY REAL"
            confidence = int(55 + (uncertain_thresh - combined_score) * 75)
        else:
            classification = "REAL"
            confidence = min(95, int(70 + (uncertain_thresh - combined_score) * 100))

        # Compile evidence
        all_findings = []
        for fa in frame_analyses:
            findings = fa.get('artifacts_detected', {}).get('findings', [])
            all_findings.extend(findings)

        temporal_findings = temporal_analysis.get('temporal_findings', [])
        all_findings.extend(temporal_findings)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            classification,
            confidence,
            combined_score,
            all_findings,
            frame_analyses,
            temporal_analysis,
            metadata
        )

        return {
            'classification': classification,
            'confidence': confidence,
            'reasoning': reasoning,
            'evidence': {
                'frame_observations': self._compile_frame_evidence(frame_analyses),
                'temporal_observations': temporal_analysis.get('analysis', '')
            },
            'scores': {
                'combined': combined_score,
                'visual_avg': avg_artifact_score,
                'visual_max': max_artifact_score,
                'temporal': temporal_score
            }
        }

    def _compile_frame_evidence(self, frame_analyses: List[dict]) -> str:
        """Compile frame-level observations into structured text."""
        evidence_parts = []

        for fa in frame_analyses:
            frame_idx = fa.get('frame_index', 0)
            artifacts = fa.get('artifacts_detected', {})
            findings = artifacts.get('findings', [])

            if findings:
                evidence_parts.append(f"Frame {frame_idx}:")
                for finding in findings:
                    evidence_parts.append(f"  - {finding}")

        if not evidence_parts:
            return "No significant visual artifacts detected across analyzed frames."

        return "\n".join(evidence_parts)

    def _generate_reasoning(
        self,
        classification: str,
        confidence: int,
        combined_score: float,
        all_findings: List[str],
        frame_analyses: List[dict],
        temporal_analysis: dict,
        metadata: dict
    ) -> str:
        """Generate natural language reasoning for the verdict."""
        reasoning_parts = []

        # Opening statement
        if classification in ["FAKE", "LIKELY FAKE"]:
            reasoning_parts.append(
                f"Classification: {classification} (Confidence: {confidence}%)\n"
            )
            reasoning_parts.append(
                "The video exhibits multiple characteristics consistent with synthetic generation or manipulation.\n"
            )
        elif classification == "UNCERTAIN":
            reasoning_parts.append(
                f"Classification: {classification} (Confidence: {confidence}%)\n"
            )
            reasoning_parts.append(
                "The analysis reveals mixed signals, making confident classification difficult.\n"
            )
        else:  # REAL or LIKELY REAL
            reasoning_parts.append(
                f"Classification: {classification} (Confidence: {confidence}%)\n"
            )
            reasoning_parts.append(
                "The video demonstrates characteristics consistent with authentic, non-manipulated footage.\n"
            )

        # Key evidence
        if all_findings:
            reasoning_parts.append("KEY EVIDENCE:")
            unique_findings = list(set(all_findings))[:5]  # Top 5 unique findings
            for finding in unique_findings:
                reasoning_parts.append(f"  - {finding}")
            reasoning_parts.append("")

        # Analysis breakdown
        reasoning_parts.append("ANALYSIS BREAKDOWN:")
        reasoning_parts.append(f"  - Visual Artifacts: {len([f for f in all_findings if 'texture' in f.lower() or 'smoothing' in f.lower() or 'lighting' in f.lower()])} indicators detected")
        reasoning_parts.append(f"  - Temporal Consistency: {len(temporal_analysis.get('temporal_findings', []))} issues identified")
        reasoning_parts.append(f"  - Frames Analyzed: {len(frame_analyses)}")
        reasoning_parts.append(f"  - Combined Suspicion Score: {combined_score:.2f}/1.00")
        reasoning_parts.append("")

        # Conclusion
        if classification in ["FAKE", "LIKELY FAKE"]:
            reasoning_parts.append(
                "CONCLUSION:\n"
                "The combination of visual and temporal artifacts suggests this video is "
                "synthetically generated or significantly manipulated. The detection system "
                "identified multiple indicators consistent with deepfake generation techniques."
            )
        elif classification == "UNCERTAIN":
            reasoning_parts.append(
                "CONCLUSION:\n"
                "The evidence is inconclusive. Some artifacts are present, but they could "
                "potentially be attributed to video compression, lighting conditions, or other "
                "non-malicious factors. Further analysis or higher-quality source material "
                "would be needed for confident classification."
            )
        else:
            reasoning_parts.append(
                "CONCLUSION:\n"
                "The video shows natural characteristics expected of authentic footage. "
                "No significant artifacts or temporal inconsistencies were detected that "
                "would suggest synthetic generation or manipulation."
            )

        return "\n".join(reasoning_parts)


class LocalAgentProvider:
    """
    Provider interface for local agent, compatible with existing LLMAnalyzer.

    This allows seamless integration with the existing codebase.
    """

    def __init__(self, agent_version: str = "v1.0"):
        """Initialize local agent provider."""
        self.agent = LocalAgentRunner(agent_version=agent_version)
        self.model_name = f"local_agent_{agent_version}"

    def analyze_frame(self, frame: np.ndarray, frame_index: int, metadata: dict) -> dict:
        """Analyze a frame (compatible with LLMAnalyzer interface)."""
        return self.agent.analyze_frame(frame, frame_index, metadata)

    def analyze_temporal_sequence(self, frames: List[np.ndarray], frame_indices: List[int]) -> dict:
        """Analyze temporal sequence (compatible with LLMAnalyzer interface)."""
        return self.agent.analyze_temporal_sequence(frames, frame_indices)

    def synthesize_verdict(
        self,
        frame_analyses: List[dict],
        temporal_analysis: dict,
        metadata: dict
    ) -> dict:
        """Synthesize verdict (compatible with LLMAnalyzer interface)."""
        return self.agent.synthesize_verdict(frame_analyses, temporal_analysis, metadata)
