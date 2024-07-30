import yaml
from pathlib import Path
from typing import Union
from dataclasses import dataclass

@dataclass
class WhoopConfig:
    username: str
    password: str
    # Add any additional fields here as needed
    # For example:
    # api_url: str = "https://api.whoop.com"
    # timeout: int = 30

def load_config(config_path: Union[str, Path]) -> WhoopConfig:
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open() as f:
        config_data = yaml.safe_load(f)

    # Check for required fields
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in config_data:
            raise ValueError(f"Missing required field in config file: {field}")

    # Check if the values are not empty
    for field in required_fields:
        if not config_data[field]:
            raise ValueError(f"Empty value for required field in config file: {field}")

    return WhoopConfig(**config_data)

def validate_date_range(start: str, end: str) -> tuple:
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    if start_date > end_date:
        raise ValueError("Start date must be earlier than end date")
    if end_date > datetime.now():
        raise ValueError("End date cannot be in the future")
    return start_date, end_date
