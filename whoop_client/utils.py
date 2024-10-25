import yaml
from pathlib import Path
from typing import Union
from dataclasses import dataclass
from datetime import datetime, time, timedelta

@dataclass
class WhoopConfig:
    username: str
    password: str

def load_config(config_path: Union[str, Path]) -> WhoopConfig:
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open() as f:
        config_data = yaml.safe_load(f)

    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in config_data:
            raise ValueError(f"Missing required field in config file: {field}")
        if not config_data[field]:
            raise ValueError(f"Empty value for required field in config file: {field}")

    return WhoopConfig(**config_data)

def config_from_credentials(username: str, password: str) -> WhoopConfig:
    if not username or not password:
        raise ValueError("Username and password cannot be empty")
    return WhoopConfig(username=username, password=password)

def format_dates(start_date: str | None, end_date: str | None) -> tuple[str, str]:
    end = datetime.combine(
        datetime.fromisoformat(end_date) if end_date else datetime.today(), time.max
    )
    start = datetime.combine(
        datetime.fromisoformat(start_date)
        if start_date
        else datetime.today() - timedelta(days=6),
        time.min,
    )

    if start > end:
        raise ValueError(
            f"Start datetime greater than end datetime: {start} > {end}"
        )

    return (
        start.isoformat() + "Z",
        end.isoformat(timespec="seconds") + "Z",
    )
