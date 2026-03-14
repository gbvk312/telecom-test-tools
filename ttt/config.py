"""
Configuration loader for the Telecom Test Toolkit.

Reads ttt.config.yaml to configure pipeline behavior, tool settings,
and output directories.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


DEFAULT_CONFIG_NAME = "ttt.config.yaml"


@dataclass
class TTTConfig:
    """Parsed configuration for the Telecom Test Toolkit."""
    log_directory: str = "./logs"
    output_directory: str = "./output"
    enabled_tools: list = field(default_factory=lambda: [
        "testwatch", "log_analyzer", "testscope", "flakiness_scorer", "report_gen"
    ])
    tool_settings: Dict[str, Any] = field(default_factory=dict)
    dashboard_port: int = 8501
    history_file: str = "historical_data.csv"
    flakiness_window: int = 14

    @classmethod
    def from_dict(cls, data: dict) -> "TTTConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def find_config(start_dir: Optional[str] = None) -> Optional[str]:
    """Search for ttt.config.yaml starting from start_dir up to root."""
    if start_dir is None:
        start_dir = os.getcwd()

    current = os.path.abspath(start_dir)
    while True:
        config_path = os.path.join(current, DEFAULT_CONFIG_NAME)
        if os.path.isfile(config_path):
            return config_path
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def load_config(config_path: Optional[str] = None) -> TTTConfig:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML config file. If None, searches
                     for ttt.config.yaml in the current directory tree.

    Returns:
        TTTConfig with loaded values, or defaults if no config found.
    """
    if config_path is None:
        config_path = find_config()

    if config_path is None or not os.path.isfile(config_path):
        return TTTConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    return TTTConfig.from_dict(raw)
