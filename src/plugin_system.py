"""
Plugin System for Deepfake Detection

Provides extensibility through a plugin architecture that allows users to:
- Register custom frame sampling strategies
- Add custom analysis hooks
- Extend the detection pipeline
"""

from typing import Dict, List, Any, Callable, Protocol, Optional
from pathlib import Path
import importlib.util
import inspect
import logging


class FrameSamplerPlugin(Protocol):
    """
    Protocol for frame sampler plugins.

    Plugins must implement this protocol to be registered as frame samplers.
    """

    name: str  # Unique plugin name
    description: str  # Human-readable description

    def sample_frames(
        self,
        total_frames: int,
        num_frames: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Sample frame indices from a video.

        Args:
            total_frames: Total number of frames in video
            num_frames: Number of frames to sample
            metadata: Optional video metadata (duration, fps, etc.)

        Returns:
            List of frame indices to extract
        """
        ...


class AnalysisHookPlugin(Protocol):
    """
    Protocol for analysis hook plugins.

    Plugins can hook into the analysis pipeline at various stages.
    """

    name: str
    description: str

    def pre_analysis_hook(
        self,
        frames: List[Any],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Called before frame analysis begins.

        Args:
            frames: List of extracted frames
            metadata: Video metadata
        """
        ...

    def post_analysis_hook(
        self,
        analyses: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Called after frame analysis completes.

        Args:
            analyses: List of analysis results
            metadata: Video metadata
        """
        ...


class PluginManager:
    """
    Central plugin manager for the deepfake detection system.

    Manages plugin registration, discovery, and execution.
    """

    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialize plugin manager.

        Args:
            plugins_dir: Directory containing plugin files
        """
        self.plugins_dir = Path(plugins_dir)
        self.frame_samplers: Dict[str, FrameSamplerPlugin] = {}
        self.analysis_hooks: Dict[str, AnalysisHookPlugin] = {}
        self.logger = logging.getLogger('PluginManager')

        # Register built-in plugins
        self._register_builtin_plugins()

    def _register_builtin_plugins(self):
        """Register built-in default plugins."""
        # Built-in frame samplers are handled by VideoProcessor
        # This method is a placeholder for future built-in plugins
        pass

    def register_frame_sampler(
        self,
        plugin: FrameSamplerPlugin,
        overwrite: bool = False
    ) -> None:
        """
        Register a custom frame sampler plugin.

        Args:
            plugin: Plugin instance implementing FrameSamplerPlugin protocol
            overwrite: Allow overwriting existing plugin with same name

        Raises:
            ValueError: If plugin name already exists and overwrite=False
        """
        if not hasattr(plugin, 'name') or not hasattr(plugin, 'sample_frames'):
            raise ValueError(
                "Plugin must have 'name' attribute and 'sample_frames' method"
            )

        if plugin.name in self.frame_samplers and not overwrite:
            raise ValueError(
                f"Frame sampler plugin '{plugin.name}' already registered. "
                f"Use overwrite=True to replace."
            )

        self.frame_samplers[plugin.name] = plugin
        self.logger.info(f"Registered frame sampler plugin: {plugin.name}")

    def register_analysis_hook(
        self,
        plugin: AnalysisHookPlugin,
        overwrite: bool = False
    ) -> None:
        """
        Register an analysis hook plugin.

        Args:
            plugin: Plugin instance implementing AnalysisHookPlugin protocol
            overwrite: Allow overwriting existing plugin with same name

        Raises:
            ValueError: If plugin name already exists and overwrite=False
        """
        if not hasattr(plugin, 'name'):
            raise ValueError("Plugin must have 'name' attribute")

        if plugin.name in self.analysis_hooks and not overwrite:
            raise ValueError(
                f"Analysis hook plugin '{plugin.name}' already registered. "
                f"Use overwrite=True to replace."
            )

        self.analysis_hooks[plugin.name] = plugin
        self.logger.info(f"Registered analysis hook plugin: {plugin.name}")

    def get_frame_sampler(self, name: str) -> Optional[FrameSamplerPlugin]:
        """
        Get a registered frame sampler by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance, or None if not found
        """
        return self.frame_samplers.get(name)

    def list_frame_samplers(self) -> List[str]:
        """
        List all registered frame sampler plugin names.

        Returns:
            List of plugin names
        """
        return list(self.frame_samplers.keys())

    def list_analysis_hooks(self) -> List[str]:
        """
        List all registered analysis hook plugin names.

        Returns:
            List of plugin names
        """
        return list(self.analysis_hooks.keys())

    def execute_pre_analysis_hooks(
        self,
        frames: List[Any],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Execute all registered pre-analysis hooks.

        Args:
            frames: List of extracted frames
            metadata: Video metadata
        """
        for name, plugin in self.analysis_hooks.items():
            try:
                if hasattr(plugin, 'pre_analysis_hook'):
                    plugin.pre_analysis_hook(frames, metadata)
            except Exception as e:
                self.logger.warning(
                    f"Pre-analysis hook '{name}' failed: {e}"
                )

    def execute_post_analysis_hooks(
        self,
        analyses: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Execute all registered post-analysis hooks.

        Args:
            analyses: List of analysis results
            metadata: Video metadata
        """
        for name, plugin in self.analysis_hooks.items():
            try:
                if hasattr(plugin, 'post_analysis_hook'):
                    plugin.post_analysis_hook(analyses, metadata)
            except Exception as e:
                self.logger.warning(
                    f"Post-analysis hook '{name}' failed: {e}"
                )

    def load_plugins_from_directory(self, directory: Optional[str] = None) -> int:
        """
        Auto-discover and load plugins from a directory.

        Searches for Python files in the plugins directory and attempts
        to load any classes that implement the plugin protocols.

        Args:
            directory: Directory to search (default: self.plugins_dir)

        Returns:
            Number of plugins successfully loaded
        """
        search_dir = Path(directory) if directory else self.plugins_dir

        if not search_dir.exists():
            self.logger.warning(f"Plugins directory not found: {search_dir}")
            return 0

        loaded_count = 0

        # Find all .py files in plugins directory
        for plugin_file in search_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue  # Skip private files

            try:
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem,
                    plugin_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find plugin classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Try to register as frame sampler
                        if hasattr(obj, 'sample_frames'):
                            try:
                                instance = obj()
                                self.register_frame_sampler(instance)
                                loaded_count += 1
                            except Exception as e:
                                self.logger.warning(
                                    f"Failed to register {name} from {plugin_file.name}: {e}"
                                )

                        # Try to register as analysis hook
                        elif hasattr(obj, 'pre_analysis_hook') or hasattr(obj, 'post_analysis_hook'):
                            try:
                                instance = obj()
                                self.register_analysis_hook(instance)
                                loaded_count += 1
                            except Exception as e:
                                self.logger.warning(
                                    f"Failed to register {name} from {plugin_file.name}: {e}"
                                )

            except Exception as e:
                self.logger.error(f"Failed to load plugin file {plugin_file.name}: {e}")

        self.logger.info(f"Loaded {loaded_count} plugins from {search_dir}")
        return loaded_count

    def get_plugin_info(self) -> Dict[str, Any]:
        """
        Get information about all registered plugins.

        Returns:
            Dictionary with plugin information
        """
        return {
            'frame_samplers': {
                name: {
                    'name': plugin.name,
                    'description': getattr(plugin, 'description', 'No description')
                }
                for name, plugin in self.frame_samplers.items()
            },
            'analysis_hooks': {
                name: {
                    'name': plugin.name,
                    'description': getattr(plugin, 'description', 'No description')
                }
                for name, plugin in self.analysis_hooks.items()
            }
        }


# Global plugin manager instance
_plugin_manager = None


def get_plugin_manager(plugins_dir: str = "plugins") -> PluginManager:
    """
    Get the global plugin manager instance (singleton pattern).

    Args:
        plugins_dir: Directory containing plugin files

    Returns:
        PluginManager instance
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugins_dir=plugins_dir)
    return _plugin_manager
