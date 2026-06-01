"""Load `.env` from project root when DATABASE_URL is not already set."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv() -> None:
    if os.environ.get("DATABASE_URL"):
        return

    root = Path(__file__).resolve().parents[3]
    env_file = root / ".env"
    if not env_file.is_file():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
