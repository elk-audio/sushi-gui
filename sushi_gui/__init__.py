import json
import os

# Global variable to hold plugins configuration
INSTALLED_PLUGINS = {}

def load_plugins_file(plugins_file_path=None):
    """Load plugins configuration from JSON file.

    Args:
        plugins_file_path: Path to plugins JSON file. If None, uses default 'installed_plugins.json'
                          in the repository root.

    Returns:
        dict: Plugins configuration dictionary
    """
    global INSTALLED_PLUGINS

    if plugins_file_path is None:
        # Default to installed_plugins.json in the repository root
        # __file__ is sushi_gui/__init__.py, so go up one level
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plugins_file_path = os.path.join(repo_root, 'installed_plugins.json')

    try:
        with open(plugins_file_path, 'r') as f:
            INSTALLED_PLUGINS = json.load(f)
        print(f"Loaded plugins from: {plugins_file_path}")
    except FileNotFoundError:
        print(f"Error: Plugins file not found at {plugins_file_path}")
        INSTALLED_PLUGINS = {"plugins": {}}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in plugins file: {e}")
        INSTALLED_PLUGINS = {"plugins": {}}

    return INSTALLED_PLUGINS

# Load default plugins file at module import
load_plugins_file()
