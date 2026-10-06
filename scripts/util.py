from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else ROOT / "config.json"
    with config_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def write_text(path: str | Path, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8", newline="\n")
