from pathlib import Path
from typing import Any, Optional

import yaml


# Class: ConfigManager
class ConfigManager:
    """Manages application configuration from YAML file

    By design this class reads configuration from a YAML file. Some runtime
    settings are intentionally provided via environment variables and read by
    the components that consume them (e.g., frontend timeout or API URL).
    See the repository `.env.example` and top-level README 'Environment'
    documentation for more details.
    """

    # Function: __init__
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    # Function: _load_config
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    # Function: get
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Example: config_manager.get("models.detection.confidence_threshold")
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    # Function: get_all
    def get_all(self) -> dict:
        """Get entire configuration dictionary"""
        return self.config
