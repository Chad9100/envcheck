from __future__ import annotations

import tomllib
from pathlib import Path


def load_toml(path: Path) -> dict:
    """Return parsed TOML, or {} if missing/invalid."""
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def load_config(root: Path) -> dict:
    """Read [tool.envcheck] from pyproject.toml, overridden by envcheck.toml."""
    cfg: dict = {}
    py = load_toml(root / "pyproject.toml")
    cfg.update(py.get("tool", {}).get("envcheck", {}) or {})
    cfg.update(load_toml(root / "envcheck.toml"))
    return cfg


def get_ports(cfg: dict) -> list[int]:
    ports = cfg.get("ports", [])
    if not isinstance(ports, list):
        return []
    return [p for p in ports if isinstance(p, int) and not isinstance(p, bool)]
