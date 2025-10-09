import yaml
from typing import Dict, Any
from pathlib import Path


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_server_config(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get('server', {})


def get_collector_config(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get('collector', {})


def get_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get('logging', {})


def get_client_config(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get('client', {})
