"""Configuration loader for ambulance pipeline."""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load pipeline configuration from YAML file.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Dictionary with configuration settings
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def get_input_directory(config: Dict[str, Any]) -> Path:
    """Get input directory path from config."""
    return Path(config['input']['directory'])


def get_output_directory(config: Dict[str, Any]) -> Path:
    """Get output directory path from config."""
    return Path(config['output']['directory'])
