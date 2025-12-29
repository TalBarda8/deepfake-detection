"""
LLM Analyzer Module

Handles LLM integration, prompt construction, and deepfake analysis
using vision-capable language models.
"""

import base64
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np
from io import BytesIO
from PIL import Image


class LLMAnalyzer:
    """
    LLM-based video analysis for deepfake detection.

    Uses vision-capable language models to analyze video frames and identify
    potential deepfake artifacts through reasoning rather than classification.
    """

    def __init__(
        self,
        api_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        prompts_dir: str = "prompts"
    ):
        """
        Initialize LLM analyzer.

        Args:
            api_provider: LLM provider ('local', 'anthropic', 'openai', or 'mock')
            model_name: Specific model to use (optional, uses default)
            api_key: API key (optional, reads from environment)
            prompts_dir: Directory containing prompt templates
        """
        self.api_provider = api_provider.lower()
        self.prompts_dir = Path(prompts_dir)

        # Set model name
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = self._get_default_model()

        # Set API key
        self.api_key = api_key or self._get_api_key()

        # Initialize API client (or local agent)
        self.client = self._initialize_client()

        # Load prompts
        self.prompts = self._load_prompts()

    def _get_default_model(self) -> str:
        """Get default model for the provider."""
        defaults = {
            'local': 'v1.0',
            'anthropic': 'claude-3-5-sonnet-20241022',
            'openai': 'gpt-4o',
            'mock': 'mock-vision-model'
        }
        return defaults.get(self.api_provider, 'v1.0')

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables."""
        env_vars = {
            'local': None,
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'mock': None
        }

        env_var = env_vars.get(self.api_provider)
        if env_var:
            return os.getenv(env_var)
        return None

    def _initialize_client(self):
        """Initialize API client based on provider."""
        if self.api_provider == 'local':
            try:
                from src.local_agent import LocalAgentProvider
                return LocalAgentProvider(agent_version=self.model_name)
            except ImportError as e:
                raise ImportError(
                    f"Local agent not found: {e}. "
                    "Ensure src/local_agent.py and agents/ directory exist."
                )

        elif self.api_provider == 'anthropic':
            try:
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. "
                    "Install with: pip install anthropic"
                )

        elif self.api_provider == 'openai':
            try:
                import openai
                return openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. "
                    "Install with: pip install openai"
                )

        elif self.api_provider == 'mock':
            return None  # Mock mode for testing without API

        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates from files."""
        prompts = {}

        # Define expected prompt files
        prompt_files = {
            'frame_analysis': 'frame_analysis.txt',
            'temporal_analysis': 'temporal_analysis.txt',
            'synthesis': 'synthesis.txt'
        }

        for key, filename in prompt_files.items():
            filepath = self.prompts_dir / filename

            if filepath.exists():
                with open(filepath, 'r') as f:
                    prompts[key] = f.read()
            else:
                # Use default inline prompts if files don't exist
                prompts[key] = self._get_default_prompt(key)

        return prompts

    def _get_default_prompt(self, prompt_type: str) -> str:
        """Get default inline prompt if file not found."""
        defaults = {
            'frame_analysis': """Analyze this video frame for signs of deepfake manipulation.

Focus on:
1. Facial features: Look for unnatural smoothing, inconsistent lighting, warping, or artifacts
2. Background: Check for blur boundaries, inconsistencies, or warping around edges
3. Texture: Identify areas that appear too smooth, synthetic, or have resolution mismatches
4. Physical plausibility: Note any physically impossible features or inconsistencies

For each observation, specify:
- What you observe
- Where in the frame (e.g., "around the jawline", "in the background")
- Why it might indicate synthetic manipulation

Provide a structured analysis with specific, concrete observations.""",

            'temporal_analysis': """Compare these consecutive video frames for temporal consistency.

Analyze:
1. Motion continuity: Are movements natural and fluid?
2. Lighting consistency: Does lighting remain consistent across frames?
3. Facial expressions: Are expression transitions natural?
4. Blinking patterns: Is blinking natural and consistent?
5. Background stability: Does the background remain stable or show artifacts?
6. Boundary artifacts: Are there flickering or warping artifacts at face boundaries?

Identify specific inconsistencies that might indicate deepfake generation, such as:
- Unnatural jitter or micro-movements
- Discontinuities in motion
- Flickering artifacts
- Inconsistent physics

Provide specific frame references (e.g., "between frames 2 and 3").""",

            'synthesis': """Based on the frame-level and temporal analyses, provide a final assessment of whether this video is likely a deepfake.

Consider the complete evidence:
- Visual artifacts identified in individual frames
- Temporal inconsistencies across frames
- Patterns consistent with known deepfake generation techniques
- Overall coherence and realism

Provide:
1. Classification: REAL, FAKE, or UNCERTAIN
2. Confidence: 0-100% (be honest about uncertainty)
3. Key evidence: The most significant observations supporting your conclusion
4. Reasoning: Clear explanation of how the evidence leads to your conclusion

If uncertain, explain what evidence points in different directions and why you cannot make a confident determination.

Be specific and reference concrete observations from the analysis."""
        }

        return defaults.get(prompt_type, "")

    def _encode_image_to_base64(self, image: np.ndarray) -> str:
        """
        Encode numpy image array to base64 string.

        Args:
            image: Image as numpy array (RGB format)

        Returns:
            Base64 encoded image string
        """
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(image.astype('uint8'), 'RGB')

        # Save to bytes buffer
        buffer = BytesIO()
        pil_image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        # Encode to base64
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        return image_base64

    def analyze_frame(
        self,
        frame: np.ndarray,
        frame_index: int,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single video frame for deepfake artifacts.

        Args:
            frame: Frame image as numpy array
            frame_index: Index of frame in video
            metadata: Optional video metadata

        Returns:
            Analysis results dictionary
        """
        # Use local agent directly if provider is 'local'
        if self.api_provider == 'local':
            return self.client.analyze_frame(frame, frame_index, metadata or {})

        # Prepare the prompt for API-based analysis
        prompt = self.prompts['frame_analysis']

        # Add metadata context if available
        if metadata:
            context = f"\n\nVideo metadata:\n"
            context += f"- Resolution: {metadata.get('resolution', 'unknown')}\n"
            context += f"- Duration: {metadata.get('duration', 'unknown')}s\n"
            context += f"- Codec: {metadata.get('codec', 'unknown')}\n"
            prompt = context + "\n" + prompt

        # Call LLM with image
        response = self._call_llm_vision(prompt, [frame])

        return {
            'frame_index': frame_index,
            'analysis': response,
            'prompt_type': 'frame_analysis'
        }

    def analyze_temporal_sequence(
        self,
        frames: List[np.ndarray],
        frame_indices: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Analyze temporal consistency across multiple frames.

        Args:
            frames: List of frame images
            frame_indices: Optional list of frame indices

        Returns:
            Temporal analysis results
        """
        # Use local agent directly if provider is 'local'
        if self.api_provider == 'local':
            return self.client.analyze_temporal_sequence(frames, frame_indices or list(range(len(frames))))

        # Prepare the prompt for API-based analysis
        prompt = self.prompts['temporal_analysis']

        # Add frame count context
        context = f"\n\nAnalyzing {len(frames)} frames from the video.\n"
        if frame_indices:
            context += f"Frame indices: {frame_indices}\n"

        prompt = context + "\n" + prompt

        # Call LLM with multiple frames
        response = self._call_llm_vision(prompt, frames[:8])  # Limit to 8 frames for API constraints

        return {
            'num_frames': len(frames),
            'frame_indices': frame_indices,
            'analysis': response,
            'prompt_type': 'temporal_analysis'
        }

    def synthesize_verdict(
        self,
        frame_analyses: List[Dict],
        temporal_analysis: Dict,
        metadata: Dict
    ) -> Dict[str, Any]:
        """
        Synthesize final verdict from all analyses.

        Args:
            frame_analyses: List of frame-level analysis results
            temporal_analysis: Temporal analysis results
            metadata: Video metadata

        Returns:
            Final verdict with classification, confidence, and reasoning
        """
        # Use local agent directly if provider is 'local'
        if self.api_provider == 'local':
            return self.client.synthesize_verdict(frame_analyses, temporal_analysis, metadata)

        # Compile evidence from analyses (for API-based analysis)
        evidence = self._compile_evidence(frame_analyses, temporal_analysis)

        # Prepare synthesis prompt
        prompt = self.prompts['synthesis']

        # Add evidence context
        context = f"""
Video: {metadata.get('filename', 'unknown')}
Duration: {metadata.get('duration', 0):.2f}s
Resolution: {metadata.get('resolution', 'unknown')}
Frames analyzed: {len(frame_analyses)}

FRAME-LEVEL OBSERVATIONS:
{evidence['frame_observations']}

TEMPORAL OBSERVATIONS:
{evidence['temporal_observations']}

"""

        full_prompt = context + "\n" + prompt

        # Call LLM for synthesis (text-only, no images needed)
        response = self._call_llm_text(full_prompt)

        # Parse the response to extract classification and confidence
        verdict = self._parse_verdict(response)

        return {
            'classification': verdict['classification'],
            'confidence': verdict['confidence'],
            'reasoning': response,
            'evidence': evidence,
            'metadata': metadata
        }

    def _compile_evidence(
        self,
        frame_analyses: List[Dict],
        temporal_analysis: Dict
    ) -> Dict[str, str]:
        """Compile evidence from analyses into structured format."""

        # Summarize frame-level observations
        frame_obs = []
        for i, analysis in enumerate(frame_analyses):
            frame_obs.append(f"Frame {analysis.get('frame_index', i)}: {analysis['analysis'][:200]}...")

        frame_observations = "\n".join(frame_obs[:5])  # Limit to first 5 for brevity

        # Temporal observations
        temporal_observations = temporal_analysis['analysis'][:500]  # Truncate if too long

        return {
            'frame_observations': frame_observations,
            'temporal_observations': temporal_observations
        }

    def _parse_verdict(self, synthesis_text: str) -> Dict[str, Any]:
        """
        Parse classification and confidence from synthesis text.

        Args:
            synthesis_text: LLM synthesis output

        Returns:
            Parsed verdict dictionary
        """
        # Default values
        classification = "UNCERTAIN"
        confidence = 50

        # Simple keyword-based parsing
        text_upper = synthesis_text.upper()

        # Determine classification
        if "CLASSIFICATION: FAKE" in text_upper or "VERDICT: FAKE" in text_upper:
            classification = "FAKE"
        elif "CLASSIFICATION: REAL" in text_upper or "VERDICT: REAL" in text_upper:
            classification = "REAL"
        elif "LIKELY FAKE" in text_upper or "PROBABLY FAKE" in text_upper:
            classification = "LIKELY FAKE"
        elif "LIKELY REAL" in text_upper or "PROBABLY REAL" in text_upper:
            classification = "LIKELY REAL"

        # Extract confidence (look for percentage)
        import re
        confidence_match = re.search(r'confidence:?\s*(\d+)%?', text_upper)
        if confidence_match:
            confidence = int(confidence_match.group(1))

        return {
            'classification': classification,
            'confidence': confidence
        }

    def _call_llm_vision(self, prompt: str, images: List[np.ndarray]) -> str:
        """
        Call LLM with vision capabilities.

        Args:
            prompt: Text prompt
            images: List of images as numpy arrays

        Returns:
            LLM response text
        """
        if self.api_provider == 'anthropic':
            return self._call_anthropic_vision(prompt, images)
        elif self.api_provider == 'openai':
            return self._call_openai_vision(prompt, images)
        elif self.api_provider == 'mock':
            return self._mock_vision_response(prompt, images)
        else:
            raise ValueError(f"Unsupported provider: {self.api_provider}")

    def _call_llm_text(self, prompt: str) -> str:
        """
        Call LLM for text-only analysis.

        Args:
            prompt: Text prompt

        Returns:
            LLM response text
        """
        if self.api_provider == 'anthropic':
            return self._call_anthropic_text(prompt)
        elif self.api_provider == 'openai':
            return self._call_openai_text(prompt)
        elif self.api_provider == 'mock':
            return self._mock_text_response(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.api_provider}")

    def _call_anthropic_vision(self, prompt: str, images: List[np.ndarray]) -> str:
        """Call Anthropic Claude with vision."""
        # Prepare image content
        image_content = []
        for img in images:
            img_b64 = self._encode_image_to_base64(img)
            image_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": img_b64
                }
            })

        # Add text prompt
        image_content.append({
            "type": "text",
            "text": prompt
        })

        # Make API call
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": image_content
            }]
        )

        return response.content[0].text

    def _call_anthropic_text(self, prompt: str) -> str:
        """Call Anthropic Claude for text-only."""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.content[0].text

    def _call_openai_vision(self, prompt: str, images: List[np.ndarray]) -> str:
        """Call OpenAI GPT-4V with vision."""
        # Prepare image content
        image_content = []
        for img in images:
            img_b64 = self._encode_image_to_base64(img)
            image_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            })

        # Add text prompt
        image_content.append({
            "type": "text",
            "text": prompt
        })

        # Make API call
        response = self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": image_content
            }]
        )

        return response.choices[0].message.content

    def _call_openai_text(self, prompt: str) -> str:
        """Call OpenAI for text-only."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.choices[0].message.content

    def _mock_vision_response(self, prompt: str, images: List[np.ndarray]) -> str:
        """Generate mock response for testing without API calls."""
        return f"""[MOCK ANALYSIS - Testing Mode]

Analyzed {len(images)} frame(s).

Frame observations:
- Facial smoothing detected in central region
- Slight lighting inconsistency between face and background
- Minor texture artifacts around jawline
- Resolution appears consistent

Overall: Some artifacts detected that could indicate synthetic generation.
"""

    def _mock_text_response(self, prompt: str) -> str:
        """Generate mock text response for testing."""
        return """[MOCK SYNTHESIS - Testing Mode]

Classification: LIKELY FAKE
Confidence: 70%

Key evidence:
- Multiple frames show facial smoothing artifacts
- Lighting inconsistencies observed
- Temporal discontinuities in motion

Reasoning: The combination of visual artifacts and temporal inconsistencies
suggests this video may be synthetically generated. However, confidence is
moderate due to limited artifact severity.
"""
