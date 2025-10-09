from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .db import ConnectionConfig

CONFIG_DIR = Path.home() / ".oracle_cli"
CONFIG_PATH = CONFIG_DIR / "config.json"


def load_config(path: Path = CONFIG_PATH) -> Optional[ConnectionConfig]:
    if not path.exists():
        return None

    try:
        raw = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    required_keys = {"user", "password", "dsn", "schema"}
    if not required_keys.issubset(raw):
        return None

    return ConnectionConfig(
        user=raw["user"],
        password=raw["password"],
        dsn=raw["dsn"],
        schema=raw["schema"],
    )


def save_config(config: ConnectionConfig, path: Path = CONFIG_PATH) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = asdict(config)
    path.write_text(json.dumps(payload, indent=2))
