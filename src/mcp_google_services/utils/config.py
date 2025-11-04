"""Configuration management for Google Services MCP Server."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager with support for files and environment variables."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        env_path: Optional[Path] = None,
    ):
        """Initialize Config.

        Args:
            config_path: Path to config.json file. If None, uses default.
            env_path: Path to .env file. If None, uses default.
        """
        # Load environment variables
        if env_path:
            load_dotenv(env_path)
        else:
            # Try default locations
            default_env = Path("config/.env")
            if default_env.exists():
                load_dotenv(default_env)
            else:
                load_dotenv()  # Try current directory
        
        # Load JSON config
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = Path("config/config.json")
        
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self._config = json.load(f)
            except Exception:
                self._config = {}
        else:
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Supports dot-notation for nested keys (e.g., "gmail.backup_folder").
        Also checks environment variables with format: KEY_NAME (uppercase, dots replaced with underscores).

        Args:
            key: Configuration key (supports dot-notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # First check environment variable
        env_key = key.replace(".", "_").upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(env_value)
            except (json.JSONDecodeError, ValueError):
                # Handle boolean strings
                if env_value.lower() == "true":
                    return True
                elif env_value.lower() == "false":
                    return False
                # Handle numeric strings
                try:
                    return int(env_value)
                except ValueError:
                    try:
                        return float(env_value)
                    except ValueError:
                        return env_value
        
        # Then check config file
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (supports dot-notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        # Save to file
        self._save_config()

    def _save_config(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration.

        Returns:
            Dictionary of all configuration values
        """
        return self._config.copy()

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

