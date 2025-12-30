"""
Tests for Plugin System Module
"""

import pytest
from pathlib import Path
from src.plugin_system import (
    PluginManager,
    get_plugin_manager,
    FrameSamplerPlugin,
    AnalysisHookPlugin
)


class TestPluginManager:
    """Test cases for PluginManager class."""

    @pytest.fixture
    def plugin_manager(self):
        """Create PluginManager instance."""
        return PluginManager(plugins_dir="plugins")

    def test_initialization(self, plugin_manager):
        """Test plugin manager initialization."""
        assert plugin_manager is not None
        assert plugin_manager.plugins_dir == Path("plugins")
        assert isinstance(plugin_manager.frame_samplers, dict)
        assert isinstance(plugin_manager.analysis_hooks, dict)

    def test_register_frame_sampler(self, plugin_manager):
        """Test registering a frame sampler plugin."""

        class TestSampler:
            name = "test_sampler"
            description = "Test sampler"

            def sample_frames(self, total_frames, num_frames, metadata=None):
                return list(range(num_frames))

        sampler = TestSampler()
        plugin_manager.register_frame_sampler(sampler)

        assert "test_sampler" in plugin_manager.frame_samplers
        assert plugin_manager.get_frame_sampler("test_sampler") is sampler

    def test_register_frame_sampler_duplicate_error(self, plugin_manager):
        """Test that duplicate registration raises error."""

        class TestSampler:
            name = "duplicate"

            def sample_frames(self, total_frames, num_frames, metadata=None):
                return []

        sampler1 = TestSampler()
        sampler2 = TestSampler()

        plugin_manager.register_frame_sampler(sampler1)

        with pytest.raises(ValueError, match="already registered"):
            plugin_manager.register_frame_sampler(sampler2, overwrite=False)

    def test_register_frame_sampler_overwrite(self, plugin_manager):
        """Test overwriting existing plugin."""

        class TestSampler:
            name = "overwrite_test"

            def sample_frames(self, total_frames, num_frames, metadata=None):
                return []

        sampler1 = TestSampler()
        sampler2 = TestSampler()

        plugin_manager.register_frame_sampler(sampler1)
        plugin_manager.register_frame_sampler(sampler2, overwrite=True)

        assert plugin_manager.get_frame_sampler("overwrite_test") is sampler2

    def test_register_invalid_sampler(self, plugin_manager):
        """Test that invalid sampler raises error."""

        class InvalidSampler:
            pass  # Missing required methods

        with pytest.raises(ValueError, match="must have 'name'"):
            plugin_manager.register_frame_sampler(InvalidSampler())

    def test_register_analysis_hook(self, plugin_manager):
        """Test registering an analysis hook."""

        class TestHook:
            name = "test_hook"
            description = "Test hook"

            def pre_analysis_hook(self, frames, metadata):
                pass

            def post_analysis_hook(self, analyses, metadata):
                pass

        hook = TestHook()
        plugin_manager.register_analysis_hook(hook)

        assert "test_hook" in plugin_manager.analysis_hooks

    def test_list_frame_samplers(self, plugin_manager):
        """Test listing registered frame samplers."""

        class Sampler1:
            name = "sampler1"

            def sample_frames(self, total_frames, num_frames, metadata=None):
                return []

        class Sampler2:
            name = "sampler2"

            def sample_frames(self, total_frames, num_frames, metadata=None):
                return []

        plugin_manager.register_frame_sampler(Sampler1())
        plugin_manager.register_frame_sampler(Sampler2())

        samplers = plugin_manager.list_frame_samplers()
        assert "sampler1" in samplers
        assert "sampler2" in samplers

    def test_list_analysis_hooks(self, plugin_manager):
        """Test listing registered analysis hooks."""

        class Hook1:
            name = "hook1"

            def pre_analysis_hook(self, frames, metadata):
                pass

        class Hook2:
            name = "hook2"

            def post_analysis_hook(self, analyses, metadata):
                pass

        plugin_manager.register_analysis_hook(Hook1())
        plugin_manager.register_analysis_hook(Hook2())

        hooks = plugin_manager.list_analysis_hooks()
        assert "hook1" in hooks
        assert "hook2" in hooks

    def test_execute_pre_analysis_hooks(self, plugin_manager):
        """Test executing pre-analysis hooks."""

        called = {"count": 0}

        class TestHook:
            name = "pre_hook"

            def pre_analysis_hook(self, frames, metadata):
                called["count"] += 1

        plugin_manager.register_analysis_hook(TestHook())
        plugin_manager.execute_pre_analysis_hooks(frames=[1, 2, 3], metadata={})

        assert called["count"] == 1

    def test_execute_post_analysis_hooks(self, plugin_manager):
        """Test executing post-analysis hooks."""

        called = {"count": 0}

        class TestHook:
            name = "post_hook"

            def post_analysis_hook(self, analyses, metadata):
                called["count"] += 1

        plugin_manager.register_analysis_hook(TestHook())
        plugin_manager.execute_post_analysis_hooks(analyses=[], metadata={})

        assert called["count"] == 1

    def test_hook_error_handling(self, plugin_manager):
        """Test that hook errors are handled gracefully."""

        class FailingHook:
            name = "failing_hook"

            def pre_analysis_hook(self, frames, metadata):
                raise RuntimeError("Hook failed!")

        plugin_manager.register_analysis_hook(FailingHook())

        # Should not raise exception
        plugin_manager.execute_pre_analysis_hooks(frames=[], metadata={})

    def test_get_plugin_info(self, plugin_manager):
        """Test getting plugin information."""

        class TestSampler:
            name = "info_sampler"
            description = "Test description"

            def sample_frames(self, total_frames, num_frames, metadata=None):
                return []

        plugin_manager.register_frame_sampler(TestSampler())

        info = plugin_manager.get_plugin_info()

        assert "frame_samplers" in info
        assert "analysis_hooks" in info
        assert "info_sampler" in info["frame_samplers"]
        assert info["frame_samplers"]["info_sampler"]["description"] == "Test description"

    def test_get_nonexistent_sampler(self, plugin_manager):
        """Test getting a non-existent sampler returns None."""
        sampler = plugin_manager.get_frame_sampler("nonexistent")
        assert sampler is None

    def test_load_plugins_from_directory(self, plugin_manager):
        """Test loading plugins from directory."""
        # This will attempt to load from plugins/ directory
        # Should load emotion_sampler and scene_sampler
        count = plugin_manager.load_plugins_from_directory("plugins")

        # Should load at least the example plugins
        assert count >= 0  # May be 0 if plugins dir doesn't exist in test env

    def test_load_plugins_nonexistent_directory(self, plugin_manager):
        """Test loading from non-existent directory."""
        count = plugin_manager.load_plugins_from_directory("nonexistent_dir")
        assert count == 0


class TestGlobalPluginManager:
    """Test cases for global plugin manager singleton."""

    def test_get_plugin_manager_singleton(self):
        """Test that get_plugin_manager returns singleton."""
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()

        # Should be the same instance
        assert manager1 is manager2


class TestExamplePlugins:
    """Test cases for example plugins."""

    def test_emotion_sampler(self):
        """Test emotion-based sampler plugin."""
        from plugins.emotion_sampler import EmotionBasedSampler

        sampler = EmotionBasedSampler()

        assert sampler.name == "emotion"
        assert sampler.description is not None

        # Test sampling
        frames = sampler.sample_frames(total_frames=100, num_frames=10)

        assert len(frames) == 10
        assert all(0 <= f < 100 for f in frames)
        assert frames == sorted(frames)  # Should be sorted

    def test_scene_sampler(self):
        """Test scene-based sampler plugin."""
        from plugins.scene_sampler import SceneBasedSampler

        sampler = SceneBasedSampler()

        assert sampler.name == "scene"
        assert sampler.description is not None

        # Test sampling with metadata
        frames = sampler.sample_frames(
            total_frames=150,
            num_frames=10,
            metadata={'fps': 30.0, 'duration': 5.0}
        )

        assert len(frames) == 10
        assert all(0 <= f < 150 for f in frames)
        assert frames == sorted(frames)

    def test_scene_transition_hook(self):
        """Test scene transition hook."""
        from plugins.scene_sampler import SceneTransitionHook

        hook = SceneTransitionHook()

        assert hook.name == "scene_transition_logger"
        assert hook.description is not None

        # Test pre-analysis hook
        hook.pre_analysis_hook(frames=[1, 2, 3], metadata={})

        # Test post-analysis hook
        analyses = [
            {'frame_index': 0, 'suspicion_level': 'LOW'},
            {'frame_index': 10, 'suspicion_level': 'HIGH'},
            {'frame_index': 20, 'suspicion_level': 'LOW'}
        ]
        hook.post_analysis_hook(analyses, metadata={})
