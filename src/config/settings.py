"""Application settings and configuration management."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment and config files."""

    # Application
    app_name: str = Field(default="stock-trading-decision-support", env="APP_NAME")
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")

    # Paths
    data_raw_path: str = Field(default="./data/raw", env="DATA_RAW_PATH")
    data_processed_path: str = Field(default="./data/processed", env="DATA_PROCESSED_PATH")
    data_features_path: str = Field(default="./data/features", env="DATA_FEATURES_PATH")
    model_saved_path: str = Field(default="./models/saved_models", env="MODEL_SAVED_PATH")
    model_scaler_path: str = Field(default="./models/scalers", env="MODEL_SCALER_PATH")
    log_path: str = Field(default="./logs", env="LOG_PATH")

    # Trading
    initial_capital: float = Field(default=100000.0, env="INITIAL_CAPITAL")
    max_position_size: float = Field(default=0.05, env="MAX_POSITION_SIZE")
    stop_loss_percent: float = Field(default=0.02, env="STOP_LOSS_PERCENT")
    take_profit_percent: float = Field(default=0.05, env="TAKE_PROFIT_PERCENT")

    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Configuration files
    config_dir: str = "config"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        """Initialize settings."""
        super().__init__(**kwargs)
        self._yaml_configs: Dict[str, Any] = {}
        self._load_yaml_configs()

    def _load_yaml_configs(self) -> None:
        """Load YAML configuration files."""
        config_files = {
            "main": "config.yaml",
            "model": "model_config.yaml",
            "trading": "trading_config.yaml",
            "logging": "logging_config.yaml",
        }

        for key, filename in config_files.items():
            filepath = os.path.join(self.config_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f:
                        self._yaml_configs[key] = yaml.safe_load(f)
                except Exception as e:
                    print(f"Warning: Failed to load {filepath}: {e}")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value from YAML configs.

        Args:
            key: Configuration key (can use dot notation, e.g., 'data.source')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        parts = key.split(".")
        config_type = parts[0] if parts[0] in self._yaml_configs else "main"

        if config_type in self._yaml_configs:
            config = self._yaml_configs[config_type]
            keys = parts if config_type == parts[0] else [config_type] + parts

            try:
                result = config
                for k in keys[1:]:  # Skip the config type
                    result = result[k]
                return result
            except (KeyError, TypeError):
                pass

        return default

    def get_yaml_config(self, config_type: str) -> Dict[str, Any]:
        """Get entire YAML configuration.

        Args:
            config_type: Type of configuration (main, model, trading, logging)

        Returns:
            Configuration dictionary
        """
        return self._yaml_configs.get(config_type, {})

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.data_raw_path,
            self.data_processed_path,
            self.data_features_path,
            self.model_saved_path,
            self.model_scaler_path,
            self.log_path,
            os.path.join(self.log_path, "application"),
            os.path.join(self.log_path, "trading"),
            os.path.join(self.log_path, "audit"),
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance
    """
    settings = Settings()
    settings.ensure_directories()
    return settings
