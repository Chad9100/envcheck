from __future__ import annotations

from pathlib import Path

from .result import FAIL, PASS, WARN, Result


def parse_keys(path: Path) -> set[str]:
    """Return the set of keys in a dotenv-style file. Values are never kept."""
    keys: set[str] = set()
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key = line.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def check_env(root: Path) -> list[Result]:
    example = root / ".env.example"
    if not example.is_file():
        return [Result("env", PASS, "no .env.example found, skipped")]
    env = root / ".env"
    if not env.is_file():
        return [Result("env", FAIL, ".env is missing (.env.example exists)")]
    want = parse_keys(example)
    have = parse_keys(env)
    results: list[Result] = []
    missing = sorted(want - have)
    extra = sorted(have - want)
    if missing:
        results.append(Result("env", FAIL, "missing keys in .env: " + ", ".join(missing)))
    else:
        results.append(Result("env", PASS, f"all {len(want)} keys from .env.example present"))
    if extra:
        results.append(Result("env", WARN, "extra keys in .env: " + ", ".join(extra)))
    return results
